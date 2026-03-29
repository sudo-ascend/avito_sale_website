from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounting.models import AccountingEntry


class DashboardViewTests(TestCase):
    def test_dashboard_renders_with_accounting_month_aggregation(self):
        user = get_user_model().objects.create_user(
            username="manager",
            password="test-pass-123",
            is_staff=True,
        )
        AccountingEntry.objects.create(
            date=timezone.localdate(),
            operation_type=AccountingEntry.OperationType.INCOME,
            category="Продажа",
            amount=Decimal("15000.00"),
        )

        self.client.force_login(user)
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["monthly_income"], Decimal("15000.00"))

    def test_dashboard_separates_subscription_income_series(self):
        user = get_user_model().objects.create_user(
            username="manager-subscription",
            password="test-pass-123",
            is_staff=True,
        )
        AccountingEntry.objects.create(
            date=timezone.localdate(),
            operation_type=AccountingEntry.OperationType.INCOME,
            source=AccountingEntry.Source.HOSTING_SUBSCRIPTION,
            category="Подписка на хостинг",
            amount=Decimal("750.00"),
        )

        self.client.force_login(user)
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["monthly_subscription_income"], Decimal("750.00"))
        self.assertIn(750.0, response.context["subscription_income_chart_data"])

    def test_old_registries_url_is_not_available(self):
        user = get_user_model().objects.create_user(
            username="manager2",
            password="test-pass-123",
            is_staff=True,
        )

        self.client.force_login(user)
        response = self.client.get("/dashboard/registries/")

        self.assertEqual(response.status_code, 404)
