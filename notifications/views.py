from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api import InternalApiTokenPermission
from core.mixins import StaffRequiredMixin

from .forms import ReminderRuleForm
from .models import NotificationLog, ReminderRule
from .services import send_expiry_notifications, send_hosting_income_notifications


class ReminderRuleListView(StaffRequiredMixin, ListView):
    model = ReminderRule
    template_name = "notifications/rule_list.html"
    context_object_name = "rules"


class ReminderRuleCreateView(StaffRequiredMixin, CreateView):
    model = ReminderRule
    form_class = ReminderRuleForm
    template_name = "notifications/rule_form.html"
    success_url = reverse_lazy("notification_rule_list")


class ReminderRuleUpdateView(StaffRequiredMixin, UpdateView):
    model = ReminderRule
    form_class = ReminderRuleForm
    template_name = "notifications/rule_form.html"
    success_url = reverse_lazy("notification_rule_list")


class NotificationLogListView(StaffRequiredMixin, ListView):
    model = NotificationLog
    template_name = "notifications/log_list.html"
    context_object_name = "logs"

    def get_queryset(self):
        queryset = NotificationLog.objects.select_related("order", "dns_target")
        event_type = self.request.GET.get("event_type")
        status = self.request.GET.get("status")
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event_type_choices"] = NotificationLog.EventType.choices
        context["status_choices"] = NotificationLog.Status.choices
        context["event_type_filter"] = self.request.GET.get("event_type", "")
        context["status_filter"] = self.request.GET.get("status", "")
        return context


class RunNotificationAPIView(APIView):
    permission_classes = [InternalApiTokenPermission]

    def post(self, request):
        return Response(
            {
                "expiry": send_expiry_notifications(),
                "hosting_income": send_hosting_income_notifications(),
            }
        )
