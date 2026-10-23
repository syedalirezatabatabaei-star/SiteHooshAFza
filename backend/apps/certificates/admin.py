from django.contrib import admin
from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_number', 'student', 'course', 'issue_date', 'status')
    list_filter = ('status',)
    search_fields = ('certificate_number', 'verification_code', 'student__phone_number')
    raw_id_fields = ('student', 'course')
    readonly_fields = ('certificate_number', 'verification_code', 'issue_date')
