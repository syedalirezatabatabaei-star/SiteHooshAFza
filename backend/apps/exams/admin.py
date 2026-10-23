from django.contrib import admin
from .models import Exam, Question, Choice, ExamAttempt, ExamAnswer


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    show_change_link = True


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'duration_minutes', 'passing_score', 'is_active', 'created_at')
    list_filter = ('is_active', 'course')
    search_fields = ('title', 'course__title')
    inlines = [QuestionInline]
    raw_id_fields = ('course',)
    list_editable = ('is_active',)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'exam', 'score', 'order')
    list_filter = ('exam',)
    inlines = [ChoiceInline]


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'score', 'passed', 'started_at', 'completed_at')
    list_filter = ('passed', 'exam')
    search_fields = ('student__phone_number', 'student__first_name')
    raw_id_fields = ('exam', 'student')
    readonly_fields = ('started_at',)
