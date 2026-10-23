"""
Seed demo data: categories, instructors, courses, and a test student.
Run:  python backend/manage.py shell --settings=config.settings_local < seed_demo.py
"""
from apps.courses.models import Category, Instructor, Course
from apps.users.models import User

# --- Test student ---
student, created = User.objects.get_or_create(
    phone_number='09120000001',
    defaults={
        'first_name': 'کاربر',
        'last_name': 'تستی',
        'role': 'STUDENT',
        'is_active': True,
    },
)
if created:
    student.set_password('Test1234!')
    student.save()

# --- Admin user ---
admin, created = User.objects.get_or_create(
    phone_number='09120000000',
    defaults={
        'first_name': 'مدیر',
        'last_name': 'سیستم',
        'role': 'ADMIN',
        'is_active': True,
        'is_staff': True,
        'is_superuser': True,
    },
)
if created:
    admin.set_password('Admin1234!')
    admin.save()

# --- Categories ---
cat_prog, _ = Category.objects.get_or_create(
    slug='programming',
    defaults={'name': 'برنامه‌نویسی', 'description': 'دوره‌های برنامه‌نویسی و توسعه نرم‌افزار'},
)
cat_ai, _ = Category.objects.get_or_create(
    slug='artificial-intelligence',
    defaults={'name': 'هوش مصنوعی', 'description': 'دوره‌های هوش مصنوعی و یادگیری ماشین'},
)
cat_data, _ = Category.objects.get_or_create(
    slug='data-science',
    defaults={'name': 'علم داده', 'description': 'تحلیل داده و علم داده'},
)

# --- Instructors ---
ins1, _ = Instructor.objects.get_or_create(
    slug='dr-ahmadi',
    defaults={
        'name': 'دکتر علی احمدی',
        'bio': 'استاد دانشگاه و متخصص هوش مصنوعی با بیش از ۱۵ سال تجربه آموزشی',
        'specialization': 'هوش مصنوعی و یادگیری ماشین',
        'education': 'دکترای هوش مصنوعی',
        'is_active': True,
    },
)
ins2, _ = Instructor.objects.get_or_create(
    slug='mr-karimi',
    defaults={
        'name': 'مهندس سارا کریمی',
        'bio': 'توسعه‌دهنده ارشد وب و مدرس برنامه‌نویسی',
        'specialization': 'برنامه‌نویسی پایتون و وب',
        'education': 'کارشناسی ارشد نرم‌افزار',
        'is_active': True,
    },
)

# --- Courses ---
courses_data = [
    {
        'slug': 'python-basics',
        'title': 'آموزش پایتون از صفر',
        'short_description': 'یادگیری زبان پایتون به صورت گام به گام از مبتدی تا پیشرفته',
        'description': 'در این دوره تمام مفاهیم پایه پایتون را به صورت پروژه‌محور یاد می‌گیرید.',
        'course_type': 'RECORDED',
        'price': 1500000,
        'category': cat_prog,
        'instructor': ins2,
    },
    {
        'slug': 'ai-fundamentals',
        'title': 'مبانی هوش مصنوعی',
        'short_description': 'آشنایی با مفاهیم پایه هوش مصنوعی و یادگیری ماشین',
        'description': 'دوره جامع هوش مصنوعی شامل یادگیری ماشین و شبکه‌های عصبی.',
        'course_type': 'RECORDED',
        'price': 2800000,
        'category': cat_ai,
        'instructor': ins1,
    },
    {
        'slug': 'data-analysis-workshop',
        'title': 'کارگاه تحلیل داده با پایتون',
        'short_description': 'کارگاه حضوری تحلیل داده با pandas و numpy',
        'description': 'کارگاه عملی تحلیل داده با تمرین‌های واقعی صنعت.',
        'course_type': 'IN_PERSON',
        'price': 3500000,
        'category': cat_data,
        'instructor': ins1,
    },
]

for c in courses_data:
    Course.objects.get_or_create(
        slug=c['slug'],
        defaults={
            'title': c['title'],
            'short_description': c['short_description'],
            'description': c['description'],
            'course_type': c['course_type'],
            'price': c['price'],
            'category': c['category'],
            'instructor': c['instructor'],
            'thumbnail': '',
            'status': 'PUBLISHED',
            'is_published': True,
        },
    )

print('Seed complete:')
print('  Users:', User.objects.count())
print('  Categories:', Category.objects.count())
print('  Instructors:', Instructor.objects.count())
print('  Courses:', Course.objects.count())
