from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'rating', 'status', 'created_at')
    list_filter = ('status', 'rating')
    search_fields = ('student__phone_number', 'student__first_name', 'course__title')
    raw_id_fields = ('course', 'student')
    list_editable = ('status',)
