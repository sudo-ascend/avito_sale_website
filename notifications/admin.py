from django.contrib import admin

from .models import NotificationLog, ReminderRule


@admin.register(ReminderRule)
class ReminderRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "days_before", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ("subject", "event_type", "recipient_email", "status", "sent_at")
    list_filter = ("event_type", "status")
    search_fields = ("subject", "message", "recipient_email", "order__title", "dns_target__domain")
