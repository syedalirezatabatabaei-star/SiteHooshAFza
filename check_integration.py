"""Run real API integration checks using a disposable database, never the site DB."""
import os
import sys
import tempfile
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.environ['DB_ENGINE'] = 'sqlite'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['JWT_SECRET_KEY'] = 'integration-test-only-secret-key-at-least-32-characters'
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'api'))
import main
from django.conf import settings
from django.db import connections
from django.core.management import call_command
from fastapi.testclient import TestClient
from apps.courses.models import Category, Instructor, Course
from apps.courses.models import Chapter, Lesson, InPersonDetail
from apps.users.models import User
from apps.enrollments.models import Enrollment
from apps.exams.models import Exam, Question, Choice
from apps.discounts.models import Coupon
from django.utils import timezone
from datetime import timedelta

original_db = ROOT / 'backend/db.sqlite3'
original_hash = hashlib.sha256(original_db.read_bytes()).hexdigest() if original_db.exists() else None
checks = []

with tempfile.TemporaryDirectory(prefix='hoosh-integration-', ignore_cleanup_errors=True) as directory:
    connections.close_all()
    settings.DATABASES['default']['NAME'] = str(Path(directory) / 'test.sqlite3')
    connections['default'].settings_dict['NAME'] = settings.DATABASES['default']['NAME']
    call_command('migrate', verbosity=0, interactive=False)
    settings.PAYMENT_GATEWAY = 'MANUAL'
    client = TestClient(main.app)
    test_media = Path(directory) / 'media'
    test_media.mkdir()
    (test_media / 'audit.txt').write_text('media route works', encoding='utf-8')
    for route in main.app.routes:
        if getattr(route, 'name', None) == 'media':
            route.app.directory = str(test_media)
            route.app.all_directories = [str(test_media)]
    assert client.get('/media/audit.txt').text == 'media route works'
    checks.append(('GET', '/media/audit.txt', 200))

    def check(method, path, expected=200, headers=None, **kwargs):
        response = client.request(method, '/api/v1' + path, headers=headers, **kwargs)
        assert response.status_code == expected, (method, path, response.status_code, response.text[:500])
        checks.append((method, path, response.status_code))
        return response.json() if response.content else None

    category = Category.objects.create(name='Audit category', slug='audit-category')
    instructor = Instructor.objects.create(name='Audit instructor', slug='audit-instructor', bio='Audit', specialization='AI')
    course = Course.objects.create(title='Audit course', slug='audit-course', instructor=instructor,
        category=category, short_description='Audit', description='Audit', course_type='RECORDED',
        price=120000, status='PUBLISHED', is_published=True)
    check('GET', '/courses/categories')
    assert check('GET', '/courses?category=audit-category')['total'] == 1
    assert check('GET', '/courses?category=missing')['total'] == 0
    assert check('GET', '/courses/audit-course')['slug'] == 'audit-course'
    check('GET', '/courses/featured')
    check('GET', '/instructors')
    check('GET', '/instructors/audit-instructor')
    check('GET', '/articles')
    check('GET', '/search?q=Audit')
    check('GET', '/cart', expected=401)
    check('GET', '/admin/dashboard/stats', expected=401)
    origin = 'http://127.0.0.1:8080'
    cors = client.options('/api/v1/courses', headers={'Origin': origin, 'Access-Control-Request-Method':'GET'})
    assert cors.status_code == 200 and cors.headers.get('access-control-allow-origin') == origin
    checks.append(('OPTIONS', 'CORS local frontend', cors.status_code))
    credentials = {'phone_number':'09129998877', 'password':'AuditPass123!'}
    token = check('POST', '/auth/register', expected=201, json={**credentials,'first_name':'Audit','last_name':'Test'})
    check('POST', '/auth/login', expected=401, json={**credentials,'password':'wrong-password'})
    token = check('POST', '/auth/login', json=credentials)
    headers = {'Authorization': 'Bearer ' + token['access_token']}
    check('POST', '/auth/refresh', json={'refresh_token':token['refresh_token']})
    check('GET', '/auth/me', headers=headers)
    check('PUT', '/users/me', headers=headers, json={'first_name':'Updated'})
    check('GET', '/admin/dashboard/stats', expected=403, headers=headers)
    check('GET', '/cart', headers=headers)
    check('POST', '/cart/items', expected=201, headers=headers, json={'course_id':course.id})
    cart = check('GET', '/cart', headers=headers)
    assert float(cart['total']) == 120000
    check('DELETE', '/cart/items/' + str(cart['items'][0]['id']), headers=headers)
    assert check('GET', '/cart', headers=headers)['items'] == []
    check('POST', '/cart/items', expected=201, headers=headers, json={'course_id':course.id})
    check('POST', '/cart/coupon', expected=400, headers=headers, json={'code':'INVALID'})
    Coupon.objects.create(code='AUDIT10', discount_type='PERCENTAGE', discount_value=10,
        start_date=timezone.now()-timedelta(days=1), end_date=timezone.now()+timedelta(days=1), max_uses=1)
    check('POST', '/cart/coupon', headers=headers, json={'code':'AUDIT10'})
    assert float(check('GET', '/cart', headers=headers)['total']) == 108000
    order = check('POST', '/orders/checkout', headers=headers)
    assert float(order['final_amount']) == 108000
    check('GET', '/orders', headers=headers)
    check('GET', '/orders/' + str(order['order_id']), headers=headers)
    check('GET', '/enrollments', headers=headers)
    check('GET', '/certificates', headers=headers)
    check('GET', '/notifications', headers=headers)
    check('GET', '/notifications/count', headers=headers)
    check('PUT', '/notifications/read-all', headers=headers)
    ticket = check('POST', '/tickets', expected=201, headers=headers, json={'subject':'Audit','message':'Audit message'})
    check('GET', '/tickets', headers=headers)
    check('GET', '/tickets/' + str(ticket['id']), headers=headers)
    check('POST', '/tickets/' + str(ticket['id']) + '/reply', headers=headers, json={'message':'Audit reply'})
    check('GET', '/reviews/course/' + str(course.id))
    admin = User.objects.create_user(phone_number='09129998878', password='AuditPass123!', role='ADMIN')
    admin_token = check('POST', '/auth/login', json={'phone_number':admin.phone_number,'password':'AuditPass123!'})
    admin_headers = {'Authorization': 'Bearer ' + admin_token['access_token']}
    for path in ['/admin/dashboard/stats','/admin/users','/admin/courses','/admin/orders','/admin/payments','/admin/discounts','/admin/reviews','/admin/tickets']:
        check('GET', path, headers=admin_headers)
    check('POST', '/payments/manual-success/' + str(order['order_id']), expected=403, headers=headers)
    check('POST', '/payments/initiate', headers=headers, json={'order_id':order['order_id']})
    check('GET', '/payments/callback?Authority=MANUAL_' + str(order['order_id']) + '&Status=OK', expected=403)
    check('POST', '/payments/manual-success/' + str(order['order_id']), headers=admin_headers)
    assert Coupon.objects.get(code='AUDIT10').used_count == 1
    check('POST', '/payments/manual-success/' + str(order['order_id']), expected=404, headers=admin_headers)
    enrollment = check('GET', '/enrollments', headers=headers)[0]
    check('GET', '/enrollments/' + str(enrollment['id']), headers=headers)
    chapter = Chapter.objects.create(course=course, title='Audit', order=1)
    lesson = Lesson.objects.create(chapter=chapter, title='Audit', order=1, duration=60)
    second_chapter = Chapter.objects.create(course=course, title='Next', order=2)
    second_lesson = Lesson.objects.create(chapter=second_chapter, title='Next', order=1, duration=60)
    progress = check('PUT', '/enrollments/' + str(enrollment['id']) + '/progress', headers=headers, json={'lesson_id':lesson.id})
    assert float(progress['progress']) == 50
    check('PUT', '/enrollments/' + str(enrollment['id']) + '/progress', headers=headers, json={'lesson_id':second_lesson.id})
    exam = Exam.objects.create(course=course, title='Audit', duration_minutes=30, passing_score=70)
    q1 = Question.objects.create(exam=exam, text='One', score=1)
    q2 = Question.objects.create(exam=exam, text='Two', score=1)
    c1 = Choice.objects.create(question=q1, text='Correct', is_correct=True)
    c2 = Choice.objects.create(question=q2, text='Correct', is_correct=True)
    check('GET', '/exams', headers=headers)
    check('GET', '/exams/' + str(exam.id), headers=headers)
    check('POST', '/exams/' + str(exam.id) + '/start', headers=headers)
    attempts = check('GET', '/exams/' + str(exam.id) + '/attempts', headers=headers)
    check('GET', '/exams/attempts/' + str(attempts[0]['id']), headers=headers)
    partial = check('POST', '/exams/' + str(exam.id) + '/submit', headers=headers, json={'answers':[{'question_id':q1.id,'choice_id':c1.id}]})
    assert float(partial['score']) == 50 and not partial['passed']
    check('POST', '/exams/' + str(exam.id) + '/start', headers=headers)
    check('POST', '/exams/' + str(exam.id) + '/submit', expected=422, headers=headers, json={'answers':[{'question_id':q1.id,'choice_id':c1.id}]*2})
    check('POST', '/exams/' + str(exam.id) + '/submit', headers=headers, json={'answers':[{'question_id':q1.id,'choice_id':c1.id},{'question_id':q2.id,'choice_id':c2.id}]})
    certificate = check('POST', '/certificates/issue/' + str(course.id), headers=headers)
    check('GET', '/certificates', headers=headers)
    assert check('GET', '/certificates/verify/' + certificate['verification_code'])['valid']
    inperson = Course.objects.create(title='In person audit', slug='in-person-audit', instructor=instructor,
        category=category, short_description='Audit', description='Audit', course_type='IN_PERSON',
        price=500000, status='PUBLISHED', is_published=True)
    InPersonDetail.objects.create(course=inperson, prepayment_amount=100000, remaining_amount=400000,
        capacity=1, start_date=timezone.now().date(), end_date=timezone.now().date()+timedelta(days=30), location='Audit')
    check('GET', '/courses/in-person-audit')
    check('POST', '/cart/items', expected=201, headers=headers, json={'course_id':inperson.id})
    ip_cart = check('GET', '/cart', headers=headers)
    assert float(ip_cart['subtotal']) == float(ip_cart['items'][0]['course_price']) == 100000
    ip_order = check('POST', '/orders/checkout', headers=headers)
    assert float(ip_order['final_amount']) == 100000
    check('POST', '/payments/manual-success/' + str(ip_order['order_id']), headers=admin_headers)
    assert inperson.inperson_detail.capacity == 1 and inperson.inperson_detail.is_full
    other_token = check('POST', '/auth/register', expected=201, json={'phone_number':'09129998879','password':'AuditPass123!','first_name':'Other','last_name':'Test'})
    other_headers = {'Authorization':'Bearer '+other_token['access_token']}
    check('POST', '/cart/items', expected=400, headers=other_headers, json={'course_id':inperson.id})
    check('GET', '/orders/' + str(order['order_id']), expected=404, headers=other_headers)
    connections.close_all()

assert original_hash == (hashlib.sha256(original_db.read_bytes()).hexdigest() if original_db.exists() else None)
print('PASS:', len(checks), 'real API checks; original database unchanged; no payment gateway called.')
if '--verbose' in sys.argv:
    for method, path, status in checks:
        print(method, path, status)
