from django.urls import path

from .views import AccountingEntryCreateView, AccountingEntryListView, AccountingEntryUpdateView

urlpatterns = [
    path("", AccountingEntryListView.as_view(), name="accounting_entry_list"),
    path("create/", AccountingEntryCreateView.as_view(), name="accounting_entry_create"),
    path("<int:pk>/edit/", AccountingEntryUpdateView.as_view(), name="accounting_entry_edit"),
]
