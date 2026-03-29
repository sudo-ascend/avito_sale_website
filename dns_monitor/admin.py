from django.contrib import admin

from .models import DNSCheckLog, DNSMonitorTarget


@admin.register(DNSMonitorTarget)
class DNSMonitorTargetAdmin(admin.ModelAdmin):
    list_display = ("domain", "record_type", "expected_value", "last_status", "last_checked_at", "is_active")
    list_filter = ("record_type", "last_status", "is_active")
    search_fields = ("domain", "expected_value", "order__title")


@admin.register(DNSCheckLog)
class DNSCheckLogAdmin(admin.ModelAdmin):
    list_display = ("target", "status", "checked_at")
    list_filter = ("status", "checked_at")
    search_fields = ("target__domain", "message")
