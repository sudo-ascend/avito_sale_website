from django.contrib import admin

from .models import AccountingEntry


@admin.register(AccountingEntry)
class AccountingEntryAdmin(admin.ModelAdmin):
    list_display = ("date", "operation_type", "source", "category", "amount", "client", "order")
    list_filter = ("operation_type", "source", "date")
    search_fields = ("category", "comment", "client__company_name", "order__title", "reference_key")
