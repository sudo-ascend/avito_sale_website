from django.contrib import admin

from .models import BriefAttachment, BriefRequest


class BriefAttachmentInline(admin.TabularInline):
    model = BriefAttachment
    extra = 0


@admin.register(BriefRequest)
class BriefRequestAdmin(admin.ModelAdmin):
    list_display = (
        "business_name",
        "client_type",
        "site_type",
        "preferred_contact_app",
        "contact_phone",
        "contact_email",
        "status",
        "created_at",
    )
    list_filter = ("status", "client_type", "site_type", "preferred_contact_app")
    search_fields = ("business_name", "contact_email", "contact_phone", "work_region")
    readonly_fields = ("created_at", "updated_at")
    inlines = (BriefAttachmentInline,)
