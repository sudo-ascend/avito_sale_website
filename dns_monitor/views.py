from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api import InternalApiTokenPermission
from core.mixins import StaffRequiredMixin

from .forms import DNSMonitorTargetForm
from .models import DNSCheckLog, DNSMonitorTarget
from .services import run_dns_checks


class DNSMonitorTargetListView(StaffRequiredMixin, ListView):
    model = DNSMonitorTarget
    template_name = "dns_monitor/target_list.html"
    context_object_name = "targets"

    def get_queryset(self):
        queryset = DNSMonitorTarget.objects.select_related("order", "order__client")
        q = self.request.GET.get("q")
        status = self.request.GET.get("status")
        if q:
            queryset = queryset.filter(
                Q(domain__icontains=q) | Q(order__title__icontains=q) | Q(order__client__company_name__icontains=q)
            )
        if status:
            queryset = queryset.filter(last_status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = DNSMonitorTarget.Status.choices
        context["status_filter"] = self.request.GET.get("status", "")
        return context


class DNSMonitorTargetCreateView(StaffRequiredMixin, CreateView):
    model = DNSMonitorTarget
    form_class = DNSMonitorTargetForm
    template_name = "dns_monitor/target_form.html"
    success_url = reverse_lazy("dns_target_list")


class DNSMonitorTargetUpdateView(StaffRequiredMixin, UpdateView):
    model = DNSMonitorTarget
    form_class = DNSMonitorTargetForm
    template_name = "dns_monitor/target_form.html"
    success_url = reverse_lazy("dns_target_list")


class DNSCheckLogListView(StaffRequiredMixin, ListView):
    model = DNSCheckLog
    template_name = "dns_monitor/log_list.html"
    context_object_name = "logs"

    def get_queryset(self):
        queryset = DNSCheckLog.objects.select_related("target", "target__order").order_by("-checked_at")
        target_id = self.request.GET.get("target")
        if target_id:
            queryset = queryset.filter(target_id=target_id)
        return queryset


class RunDNSCheckAPIView(APIView):
    permission_classes = [InternalApiTokenPermission]

    def post(self, request):
        return Response(run_dns_checks())
