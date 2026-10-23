from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'order', 'amount', 'payment_type', 'gateway', 'status', 'transaction_id', 'created_at', 'paid_at')
    list_filter = ('status', 'gateway', 'payment_type')
    search_fields = ('user__phone_number', 'transaction_id', 'authority')
    raw_id_fields = ('order', 'user')
    readonly_fields = ('created_at', 'paid_at', 'extra_data')
