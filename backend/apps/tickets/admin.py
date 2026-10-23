from django.contrib import admin
from .models import Ticket, TicketMessage


class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 0
    readonly_fields = ('sender', 'message', 'is_read', 'created_at')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'status', 'priority', 'created_at', 'updated_at')
    list_filter = ('status', 'priority')
    search_fields = ('subject', 'user__phone_number')
    raw_id_fields = ('user',)
    inlines = [TicketMessageInline]
    list_editable = ('status',)


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'sender', 'is_read', 'created_at')
    list_filter = ('is_read',)
    raw_id_fields = ('ticket', 'sender')
