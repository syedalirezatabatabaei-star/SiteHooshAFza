from django.contrib import admin
from .models import BlogCategory, Tag, Article


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'view_count', 'published_at', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    raw_id_fields = ('author', 'category')
    list_editable = ('status',)
    fieldsets = (
        ('اطلاعات اصلی', {'fields': ('title', 'slug', 'excerpt', 'content', 'featured_image', 'author', 'category', 'tags', 'status', 'published_at')}),
        ('SEO', {'fields': ('meta_title', 'meta_description', 'canonical_url', 'og_title', 'og_description'), 'classes': ('collapse',)}),
    )
