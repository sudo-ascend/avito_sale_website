from django.contrib import admin

from .models import PricingSettings


@admin.register(PricingSettings)
class PricingSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "updated_at")
