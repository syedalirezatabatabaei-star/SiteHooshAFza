from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('course', 'added_at')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'coupon', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('user__phone_number', 'user__first_name')
    inlines = [CartItemInline]
    raw_id_fields = ('user', 'coupon')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'course', 'added_at')
    raw_id_fields = ('cart', 'course')
