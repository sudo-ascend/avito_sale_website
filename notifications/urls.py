from django.urls import path

from .views import (
    NotificationLogListView,
    ReminderRuleCreateView,
    ReminderRuleListView,
    ReminderRuleUpdateView,
    RunNotificationAPIView,
)

urlpatterns = [
    path("rules/", ReminderRuleListView.as_view(), name="notification_rule_list"),
    path("rules/create/", ReminderRuleCreateView.as_view(), name="notification_rule_create"),
    path("rules/<int:pk>/edit/", ReminderRuleUpdateView.as_view(), name="notification_rule_edit"),
    path("logs/", NotificationLogListView.as_view(), name="notification_log_list"),
    path("api/internal/notifications/run/", RunNotificationAPIView.as_view(), name="notifications_run_api"),
]
