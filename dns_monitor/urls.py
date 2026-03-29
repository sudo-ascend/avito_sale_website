from django.urls import path

from .views import (
    DNSCheckLogListView,
    DNSMonitorTargetCreateView,
    DNSMonitorTargetListView,
    DNSMonitorTargetUpdateView,
    RunDNSCheckAPIView,
)

urlpatterns = [
    path("", DNSMonitorTargetListView.as_view(), name="dns_target_list"),
    path("create/", DNSMonitorTargetCreateView.as_view(), name="dns_target_create"),
    path("<int:pk>/edit/", DNSMonitorTargetUpdateView.as_view(), name="dns_target_edit"),
    path("logs/", DNSCheckLogListView.as_view(), name="dns_log_list"),
    path("api/internal/dns-check/", RunDNSCheckAPIView.as_view(), name="dns_run_api"),
]
