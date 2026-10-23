from django.contrib import admin
from .models import Enrollment


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'progress', 'enrolled_at', 'access_start', 'access_end')
    list_filter = ('status', 'course__course_type')
    search_fields = ('student__phone_number', 'student__first_name', 'student__last_name', 'course__title')
    raw_id_fields = ('student', 'course', 'last_lesson')
    list_editable = ('status',)
