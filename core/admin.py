from django.contrib import admin

from .models import SiteContent


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ("company_name", "email", "phone", "updated_at")

    fieldsets = (
        (
            "Контакты",
            {
                "fields": (
                    "company_name",
                    "company_tagline",
                    "email",
                    "phone",
                    "telegram",
                    "whatsapp",
                    "address",
                    "working_hours",
                    "map_embed_url",
                )
            },
        ),
        (
            "Менеджеры",
            {
                "fields": (
                    "primary_manager_name",
                    "secondary_manager_name",
                    "secondary_manager_phone",
                )
            },
        ),
        ("Футер", {"fields": ("footer_description",)}),
        (
            "Кейс на главной",
            {
                "fields": (
                    "home_case_kicker",
                    "home_case_title",
                    "home_case_body",
                    "home_case_image_primary",
                    "home_case_image_primary_alt",
                    "home_case_image_secondary",
                    "home_case_image_secondary_alt",
                )
            },
        ),
        (
            "Как работаем",
            {
                "fields": (
                    "process_section_kicker",
                    "process_section_title",
                    "process_step_1_title",
                    "process_step_1_body",
                    "process_step_2_title",
                    "process_step_2_body",
                    "process_step_3_title",
                    "process_step_3_body",
                    "process_step_4_title",
                    "process_step_4_body",
                    "process_highlight_label",
                    "process_highlight_value",
                    "process_highlight_body",
                    "process_cta_kicker",
                    "process_cta_title",
                    "process_cta_body",
                )
            },
        ),
        (
            "Страница контактов",
            {
                "fields": (
                    "contact_page_kicker",
                    "contact_page_title",
                    "contact_page_cta_kicker",
                    "contact_page_cta_title",
                    "contact_page_cta_body",
                    "contact_page_cta_button",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        return not SiteContent.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
