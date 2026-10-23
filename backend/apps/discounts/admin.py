from django.contrib import admin
from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'start_date', 'end_date', 'max_uses', 'used_count', 'is_active')
    list_filter = ('is_active', 'discount_type')
    search_fields = ('code',)
    filter_horizontal = ('applicable_courses',)
    list_editable = ('is_active',)
