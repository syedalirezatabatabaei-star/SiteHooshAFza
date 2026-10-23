from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class BlogCategoryResponse(BaseModel):
    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True


class TagResponse(BaseModel):
    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    id: int
    title: str
    slug: str
    excerpt: str
    featured_image: Optional[str] = None
    author_name: str = ''
    category: Optional[BlogCategoryResponse] = None
    published_at: Optional[datetime] = None
    view_count: int = 0

    class Config:
        from_attributes = True


class ArticleDetailResponse(BaseModel):
    id: int
    title: str
    slug: str
    excerpt: str
    content: str
    featured_image: Optional[str] = None
    author_name: str = ''
    category: Optional[BlogCategoryResponse] = None
    tags: List[TagResponse] = []
    published_at: Optional[datetime] = None
    view_count: int = 0
    meta_title: str = ''
    meta_description: str = ''
    og_title: str = ''
    og_description: str = ''

    class Config:
        from_attributes = True
