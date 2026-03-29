from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from crm.models import Client, Order

from .models import AccountingEntry


class AccountingRegistrySearchTests(TestCase):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(
            username="manager",
            password="test-pass-123",
            is_staff=True,
        )
        self.client.force_login(self.user)

    def test_entry_list_filters_by_single_search_field(self):
        crm_client = Client.objects.create(
            name="Иван Иванов",
            company_name="Ромашка",
            email="ivan@example.com",
            phone="+79991234567",
        )
        order = Order.objects.create(
            client=crm_client,
            title="Лендинг",
            start_date="2026-03-28",
            price=Decimal("10000.00"),
        )
        AccountingEntry.objects.create(
            date="2026-03-28",
            operation_type=AccountingEntry.OperationType.INCOME,
            category="Предоплата",
            amount=Decimal("10000.00"),
            client=crm_client,
            order=order,
        )
        AccountingEntry.objects.create(
            date="2026-03-28",
            operation_type=AccountingEntry.OperationType.EXPENSE,
            category="Хостинг",
            amount=Decimal("1000.00"),
        )

        response = self.client.get(reverse("accounting_entry_list"), {"q": "Предоплата"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["entries"].values_list("category", flat=True)), ["Предоплата"])

    def test_entry_list_uses_row_link_and_hides_totals(self):
        crm_client = Client.objects.create(
            name="Иван Иванов",
            company_name="Ромашка",
            email="ivan@example.com",
            phone="+79991234567",
        )
        entry = AccountingEntry.objects.create(
            date="2026-03-28",
            operation_type=AccountingEntry.OperationType.INCOME,
            category="Предоплата",
            amount=Decimal("10000.00"),
            client=crm_client,
        )

        response = self.client.get(reverse("accounting_entry_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("accounting_entry_edit", args=[entry.pk]))
        self.assertContains(response, "table-row-link")
        self.assertNotContains(response, "summary-card")
        self.assertNotContains(response, "<strong>Прибыль", html=False)
        self.assertNotContains(response, 'name="date"')
        self.assertNotContains(response, 'name="category"')
        self.assertNotContains(response, 'name="client"')

    def test_entry_can_be_created_from_registry_modal_form(self):
        crm_client = Client.objects.create(
            name="Иван Иванов",
            company_name="Ромашка",
            email="ivan@example.com",
            phone="+79991234567",
        )
        order = Order.objects.create(
            client=crm_client,
            title="Лендинг",
            start_date="2026-03-28",
            price=Decimal("10000.00"),
        )

        response = self.client.post(
            reverse("accounting_entry_list"),
            {
                "operation_type": AccountingEntry.OperationType.INCOME,
                "amount": "10000.00",
                "order": order.pk,
                "comment": "Оплата из модального окна",
                "next": reverse("accounting_entry_list"),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(AccountingEntry.objects.count(), 1)
        entry = AccountingEntry.objects.get()
        self.assertEqual(entry.date, timezone.localdate())
        self.assertEqual(entry.category, "Лендинг")
        self.assertEqual(entry.client_id, crm_client.pk)
