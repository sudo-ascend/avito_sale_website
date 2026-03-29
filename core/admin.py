from django.contrib import admin

from .models import ContactInfo, Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active", "updated_at")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "short_description", "description")


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ("company_name", "email", "phone", "is_primary", "updated_at")
    list_filter = ("is_primary",)
    search_fields = ("company_name", "email", "phone")
