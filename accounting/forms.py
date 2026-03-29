from django import forms
from django.utils import timezone

from core.forms import BaseStyledModelForm

from .models import AccountingEntry


class AccountingEntryForm(BaseStyledModelForm):
    class Meta:
        model = AccountingEntry
        fields = ("date", "operation_type", "category", "amount", "client", "order", "comment")
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "comment": forms.Textarea(attrs={"rows": 4}),
        }


class AccountingEntryQuickCreateForm(BaseStyledModelForm):
    class Meta:
        model = AccountingEntry
        fields = ("operation_type", "amount", "order", "comment")
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 4}),
        }

    def save(self, commit=True):
        entry = super().save(commit=False)
        entry.date = timezone.localdate()
        entry.client = entry.order.client if entry.order else None
        entry.category = entry.order.title[:150] if entry.order else entry.get_operation_type_display()
        if commit:
            entry.save()
            self.save_m2m()
        return entry
