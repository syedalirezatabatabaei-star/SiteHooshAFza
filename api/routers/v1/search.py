from fastapi import APIRouter, Query
from django.db.models import Q

from apps.courses.models import Course, Instructor
from apps.blog.models import Article

router = APIRouter()


@router.get('')
def search(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
):
    """جستجو در دوره‌ها، مقالات و مدرسین"""
    results = {'courses': [], 'articles': [], 'instructors': []}
    total = 0

    # Search courses
    courses = Course.objects.filter(
        Q(title__icontains=q) | Q(short_description__icontains=q),
        status='PUBLISHED', is_published=True,
    ).select_related('instructor')[:10]
    for c in courses:
        results['courses'].append({
            'id': c.id, 'title': c.title, 'slug': c.slug,
            'type': 'course', 'thumbnail': c.thumbnail.url if c.thumbnail else None,
            'instructor': c.instructor.name,
        })
    total += len(results['courses'])

    # Search articles
    articles = Article.objects.filter(
        Q(title__icontains=q) | Q(excerpt__icontains=q),
        status='PUBLISHED',
    )[:10]
    for a in articles:
        results['articles'].append({
            'id': a.id, 'title': a.title, 'slug': a.slug,
            'type': 'article', 'excerpt': a.excerpt,
        })
    total += len(results['articles'])

    # Search instructors
    instructors = Instructor.objects.filter(
        Q(name__icontains=q) | Q(specialization__icontains=q),
        is_active=True,
    )[:10]
    for i in instructors:
        results['instructors'].append({
            'id': i.id, 'name': i.name, 'slug': i.slug,
            'type': 'instructor', 'specialization': i.specialization,
        })
    total += len(results['instructors'])

    return {'query': q, 'total': total, 'results': results}
