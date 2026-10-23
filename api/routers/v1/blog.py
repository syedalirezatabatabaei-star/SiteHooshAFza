from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import math

from schemas.v1.blog import ArticleListResponse, ArticleDetailResponse, BlogCategoryResponse, TagResponse
from apps.blog.models import Article, BlogCategory, Tag

router = APIRouter()


def serialize_article_list(article) -> ArticleListResponse:
    return ArticleListResponse(
        id=article.id, title=article.title, slug=article.slug,
        excerpt=article.excerpt,
        featured_image=article.featured_image.url if article.featured_image else None,
        author_name=f'{article.author.first_name} {article.author.last_name}' if article.author else '',
        category=BlogCategoryResponse(
            id=article.category.id, name=article.category.name, slug=article.category.slug,
        ) if article.category else None,
        published_at=article.published_at,
        view_count=article.view_count,
    )


@router.get('')
def list_articles(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
):
    """لیست مقالات"""
    from django.db.models import Q
    qs = Article.objects.filter(status='PUBLISHED').select_related('author', 'category')

    if category:
        qs = qs.filter(category__slug=category)
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(excerpt__icontains=search))

    total = qs.count()
    pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    articles = qs[offset:offset + page_size]

    return {
        'items': [serialize_article_list(a) for a in articles],
        'total': total, 'page': page, 'pages': pages, 'page_size': page_size,
    }


@router.get('/categories')
def list_categories():
    """دسته‌بندی مقالات"""
    cats = BlogCategory.objects.all()
    return [BlogCategoryResponse(id=c.id, name=c.name, slug=c.slug) for c in cats]


@router.get('/{slug}')
def get_article(slug: str):
    """جزئیات مقاله"""
    try:
        article = Article.objects.select_related('author', 'category').get(slug=slug, status='PUBLISHED')
    except Article.DoesNotExist:
        raise HTTPException(status_code=404, detail='مقاله یافت نشد')

    article.view_count += 1
    article.save(update_fields=['view_count'])

    tags = [TagResponse(id=t.id, name=t.name, slug=t.slug) for t in article.tags.all()]

    return ArticleDetailResponse(
        id=article.id, title=article.title, slug=article.slug,
        excerpt=article.excerpt, content=article.content,
        featured_image=article.featured_image.url if article.featured_image else None,
        author_name=f'{article.author.first_name} {article.author.last_name}' if article.author else '',
        category=BlogCategoryResponse(
            id=article.category.id, name=article.category.name, slug=article.category.slug,
        ) if article.category else None,
        tags=tags,
        published_at=article.published_at,
        view_count=article.view_count,
        meta_title=article.meta_title, meta_description=article.meta_description,
        og_title=article.og_title, og_description=article.og_description,
    )
