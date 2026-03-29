from django.contrib import admin

from .forms import OrderForm
from .models import Client, HostingSubscription, Order


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("company_name", "name", "preferred_contact_app", "email", "phone")
    list_filter = ("preferred_contact_app",)
    search_fields = ("company_name", "name", "email", "phone")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderForm
    list_display = ("title", "client", "status", "payment_status", "next_payment_date", "price")
    list_filter = ("status", "payment_status")
    search_fields = ("title", "client__company_name", "domain")
    readonly_fields = ("created_at", "updated_at", "server_password_encrypted")


@admin.register(HostingSubscription)
class HostingSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("order", "monthly_amount", "start_date", "next_income_date", "end_date", "is_active")
    list_filter = ("is_active",)
    search_fields = ("order__title", "order__client__company_name", "order__domain")
