from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from accounting.models import AccountingEntry
from crm.models import Client, HostingSubscription, Order

from .models import NotificationLog
from .services import send_hosting_income_notifications


class HostingIncomeNotificationTests(TestCase):
    def test_monthly_hosting_income_creates_notification_and_accounting_entry(self):
        crm_client = Client.objects.create(
            name="Иван Иванов",
            company_name="Ромашка",
            email="ivan@example.com",
            phone="+79991234567",
        )
        order = Order.objects.create(
            client=crm_client,
            title="Лендинг для Ромашки",
            start_date=timezone.localdate(),
            price=Decimal("10000.00"),
            payment_status=Order.PaymentStatus.PAID,
        )
        subscription = HostingSubscription.objects.create(
            order=order,
            monthly_amount=Decimal("750.00"),
            start_date=timezone.localdate(),
            next_income_date=timezone.localdate(),
            end_date=timezone.localdate() + timedelta(days=120),
            is_active=True,
        )

        result = send_hosting_income_notifications()

        subscription.refresh_from_db()
        self.assertEqual(result["sent"], 1)
        self.assertTrue(
            AccountingEntry.objects.filter(
                reference_key=f"hosting-income:{subscription.pk}:{timezone.localdate().isoformat()}",
                source=AccountingEntry.Source.HOSTING_SUBSCRIPTION,
            ).exists()
        )
        self.assertTrue(
            NotificationLog.objects.filter(
                reference_key=f"hosting-income:{subscription.pk}:{timezone.localdate().isoformat()}",
                event_type=NotificationLog.EventType.HOSTING_INCOME,
            ).exists()
        )
        self.assertGreater(subscription.next_income_date, timezone.localdate())
