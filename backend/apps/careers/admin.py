from django.contrib import admin
from .models import CareerApplication


@admin.register(CareerApplication)
class CareerApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'application_type', 'position', 'phone', 'status', 'created_at')
    list_filter = ('application_type', 'status', 'created_at')
    search_fields = ('full_name', 'phone', 'email', 'organization', 'position')
    readonly_fields = ('created_at',)
    list_editable = ('status',)
