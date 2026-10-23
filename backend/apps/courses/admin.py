from django.contrib import admin
from .models import Category, Instructor, Course, CourseSchedule, InPersonDetail, Chapter, Lesson, SpotPlayerLicense


class CourseScheduleInline(admin.TabularInline):
    model = CourseSchedule
    extra = 1


class InPersonDetailInline(admin.StackedInline):
    model = InPersonDetail
    can_delete = False
    extra = 0


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 0
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'specialization', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'specialization')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'course_type', 'instructor', 'category', 'price', 'status', 'is_published', 'spotplayer_course_id', 'created_at')
    list_filter = ('course_type', 'status', 'is_published', 'category')
    search_fields = ('title', 'slug', 'spotplayer_course_id')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CourseScheduleInline, InPersonDetailInline, ChapterInline]
    list_editable = ('status', 'is_published')


@admin.register(SpotPlayerLicense)\nclass SpotPlayerLicenseAdmin(admin.ModelAdmin):\n    list_display = ('order_item', 'external_license_id', 'status', 'created_at')\n    list_filter = ('status', 'created_at')\n    search_fields = ('external_license_id', 'order_item__order__user__phone_number')\n    readonly_fields = ('created_at', 'updated_at', 'provider_response')\n\n\n@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'chapter', 'order', 'duration', 'is_preview', 'is_published')
    list_filter = ('is_published', 'is_preview', 'chapter__course')
    search_fields = ('title',)
    list_editable = ('order', 'is_published')
