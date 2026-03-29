from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from core.mixins import StaffRequiredMixin

from .forms import AccountingEntryForm, AccountingEntryQuickCreateForm
from .models import AccountingEntry


class AccountingEntryListView(StaffRequiredMixin, ListView):
    model = AccountingEntry
    template_name = "accounting/entry_list.html"
    context_object_name = "entries"
    form_class = AccountingEntryQuickCreateForm

    def get_queryset(self):
        queryset = AccountingEntry.objects.select_related("client", "order")
        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(
                Q(category__icontains=q)
                | Q(comment__icontains=q)
                | Q(client__company_name__icontains=q)
                | Q(client__name__icontains=q)
                | Q(order__title__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["entry_form"] = kwargs.get("entry_form") or self.form_class()
        context["open_create_modal"] = kwargs.get("open_create_modal", False)
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Операция сохранена.")
            next_url = request.POST.get("next") or reverse_lazy("accounting_entry_list")
            return redirect(next_url)

        self.object_list = self.get_queryset()
        context = self.get_context_data(entry_form=form, open_create_modal=True)
        return self.render_to_response(context)


class AccountingEntryCreateView(StaffRequiredMixin, CreateView):
    model = AccountingEntry
    form_class = AccountingEntryForm
    template_name = "accounting/entry_form.html"
    success_url = reverse_lazy("accounting_entry_list")


class AccountingEntryUpdateView(StaffRequiredMixin, UpdateView):
    model = AccountingEntry
    form_class = AccountingEntryForm
    template_name = "accounting/entry_form.html"
    success_url = reverse_lazy("accounting_entry_list")
