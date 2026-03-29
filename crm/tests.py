from datetime import timedelta
import tempfile
import zipfile
from decimal import Decimal
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounting.models import AccountingEntry
from briefs.models import BriefAttachment, BriefRequest

from .models import Client, HostingSubscription, Order


SMALL_GIF = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
    b"\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00"
    b"\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
class CRMTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.media_root = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_root.name)
        self.settings_override.enable()
        self.staff_user = get_user_model().objects.create_user(
            username="manager",
            password="test-pass-123",
            is_staff=True,
        )
        self.client.force_login(self.staff_user)

    def tearDown(self):
        self.settings_override.disable()
        self.media_root.cleanup()
        super().tearDown()


class CRMRegistrySearchTests(CRMTestCase):
    def test_client_registry_redirects_to_combined_registry(self):
        response = self.client.get(reverse("crm_client_list"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("crm_order_list"))

    def test_combined_registry_filters_by_client_search_query(self):
        first_client = Client.objects.create(
            name="Иван Иванов",
            company_name="Ромашка",
            email="ivan@example.com",
            phone="+79991234567",
        )
        second_client = Client.objects.create(
            name="Петр Петров",
            company_name="Лютик",
            email="petr@example.com",
            phone="+79997654321",
        )
        Order.objects.create(
            client=first_client,
            title="Лендинг для Ромашки",
            start_date=timezone.localdate(),
            price=Decimal("10000.00"),
        )
        Order.objects.create(
            client=second_client,
            title="Каталог Лютик",
            start_date=timezone.localdate(),
            price=Decimal("12000.00"),
        )

        response = self.client.get(reverse("crm_order_list"), {"q": "Ромашка"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["orders"].values_list("client__company_name", flat=True)), ["Ромашка"])

    def test_combined_registry_rows_link_to_client_page_and_search_has_no_placeholder(self):
        crm_client = Client.objects.create(
            name="Иван Иванов",
            company_name="Ромашка",
            email="ivan@example.com",
            phone="+79991234567",
            status=Client.Status.DNS_PENDING,
        )
        order = Order.objects.create(
            client=crm_client,
            title="Лендинг для Ромашки",
            start_date=timezone.localdate(),
            price=Decimal("10000.00"),
        )

        response = self.client.get(reverse("crm_order_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order.get_absolute_url())
        self.assertNotContains(response, 'placeholder="')
        self.assertNotContains(response, "Статус клиента")

    def test_order_list_filters_by_search_query(self):
        first_client = Client.objects.create(
            name="Иван Иванов",
            company_name="Ромашка",
            email="ivan@example.com",
            phone="+79991234567",
        )
        second_client = Client.objects.create(
            name="Петр Петров",
            company_name="Лютик",
            email="petr@example.com",
            phone="+79997654321",
        )
        Order.objects.create(
            client=first_client,
            title="Лендинг для Ромашки",
            start_date=timezone.localdate(),
            price=Decimal("10000.00"),
        )
        Order.objects.create(
            client=second_client,
            title="Каталог Лютик",
            start_date=timezone.localdate(),
            price=Decimal("12000.00"),
        )

        response = self.client.get(reverse("crm_order_list"), {"q": "Лендинг"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["orders"].values_list("title", flat=True)), ["Лендинг для Ромашки"])

    def test_order_list_rows_link_to_client_page(self):
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
        )

        response = self.client.get(reverse("crm_order_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order.get_absolute_url())
        self.assertContains(response, "table-row-link")
        self.assertContains(response, crm_client.company_name)

    def test_order_status_can_be_changed_from_registry(self):
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
            status=Order.Status.NEW,
        )

        response = self.client.post(
            reverse("crm_order_status_update", args=[order.pk]),
            {"status": Order.Status.DNS_PENDING, "next": reverse("crm_order_list")},
        )

        order.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(order.status, Order.Status.DNS_PENDING)

    def test_order_detail_redirects_to_client_page(self):
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
        )

        response = self.client.get(reverse("crm_order_detail", args=[order.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, order.get_absolute_url(), fetch_redirect_response=False)


class ClientMaterialsTests(CRMTestCase):
    def setUp(self):
        super().setUp()
        self.crm_client = Client.objects.create(
            name="Иван Иванов",
            company_name="Ромашка",
            email="ivan@example.com",
            phone="+79991234567",
        )
        self.brief = BriefRequest.objects.create(
            business_name="Ромашка",
            work_region="Москва",
            contact_phone="+79991234567",
            contact_email="ivan@example.com",
            reference_sites="https://example.com",
            desired_domain="site.ru",
            logo=SimpleUploadedFile("logo.gif", SMALL_GIF, content_type="image/gif"),
        )
        BriefAttachment.objects.create(
            brief=self.brief,
            category=BriefAttachment.Category.PHOTOS,
            file=SimpleUploadedFile("photo-1.gif", SMALL_GIF, content_type="image/gif"),
        )
        BriefAttachment.objects.create(
            brief=self.brief,
            category=BriefAttachment.Category.TEXTS,
            file=SimpleUploadedFile("text-1.txt", b"text-1", content_type="text/plain"),
        )
        BriefAttachment.objects.create(
            brief=self.brief,
            category=BriefAttachment.Category.REVIEWS,
            file=SimpleUploadedFile("review-1.txt", b"review-1", content_type="text/plain"),
        )
        Order.objects.create(
            client=self.crm_client,
            brief=self.brief,
            title="Лендинг для Ромашки",
            start_date=timezone.localdate(),
            price=Decimal("10000.00"),
        )

    def test_client_edit_page_shows_materials_section(self):
        response = self.client.get(reverse("crm_client_edit", args=[self.crm_client.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Проекты и заказы")
        self.assertContains(response, "Лендинг для Ромашки")
        self.assertContains(response, "10000,00 ₽")
        self.assertContains(response, "Желаемый домен")
        self.assertContains(response, "site.ru")
        self.assertContains(response, "Login")
        self.assertContains(response, "IP")
        self.assertContains(response, "Контент")
        self.assertContains(response, "Скачать все материалы")
        self.assertContains(response, "Файлы")
        self.assertContains(response, "Тексты")
        self.assertContains(response, "Отзывы")
        self.assertContains(response, "Логотип")
        self.assertContains(response, "photo-1.gif")
        self.assertContains(response, "text-1.txt")
        self.assertNotContains(response, 'name="status"')
        self.assertNotContains(response, "Назад")

    def test_client_edit_page_hides_orders_section_when_client_has_no_orders(self):
        lonely_client = Client.objects.create(
            name="Петр Петров",
            company_name="Без заказов",
            email="petr@example.com",
            phone="+79997654321",
        )

        response = self.client.get(reverse("crm_client_edit", args=[lonely_client.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Проекты и заказы")

    def test_client_materials_download_returns_zip_archive(self):
        response = self.client.get(reverse("crm_client_materials_download", args=[self.crm_client.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")

        archive = zipfile.ZipFile(BytesIO(response.content))
        archive_names = set(archive.namelist())
        self.assertIn(f"brief-{self.brief.pk}/photos/photo-1.gif", archive_names)
        self.assertIn(f"brief-{self.brief.pk}/texts/text-1.txt", archive_names)
        self.assertIn(f"brief-{self.brief.pk}/reviews/review-1.txt", archive_names)
        self.assertIn(f"brief-{self.brief.pk}/logo/logo.gif", archive_names)


class OrderAccountingFlowTests(CRMTestCase):
    def test_paid_order_creates_project_income_entry(self):
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
            payment_status=Order.PaymentStatus.UNPAID,
        )

        response = self.client.post(
            reverse("crm_order_edit", args=[order.pk]),
            {
                "display_name": "Ромашка",
                "client_type": Client.ClientType.INDIVIDUAL,
                "status": Order.Status.COMPLETED,
                "payment_status": Order.PaymentStatus.PAID,
                "price": "10000.00",
                "start_date": timezone.localdate().isoformat(),
                "subscription_term_days": "14",
                "end_date": "",
            },
        )

        order.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(order.payment_status, Order.PaymentStatus.PAID)
        entry = AccountingEntry.objects.get(reference_key=f"project-payment:{order.pk}")
        self.assertEqual(entry.source, AccountingEntry.Source.PROJECT_PAYMENT)
        self.assertEqual(entry.amount, Decimal("10000.00"))
        self.assertEqual(entry.order_id, order.pk)

    def test_hosting_subscription_is_saved_from_order_edit_form(self):
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
        )
        next_income_date = timezone.localdate()
        end_date = timezone.localdate() + timedelta(days=90)

        response = self.client.post(
            reverse("crm_order_edit", args=[order.pk]),
            {
                "display_name": "Ромашка",
                "client_type": Client.ClientType.INDIVIDUAL,
                "status": Order.Status.COMPLETED,
                "payment_status": Order.PaymentStatus.PAID,
                "price": "10000.00",
                "start_date": timezone.localdate().isoformat(),
                "subscription_term_days": "14",
                "end_date": "",
                "has_hosting_subscription": "on",
                "hosting_monthly_amount": "750.00",
                "hosting_start_date": timezone.localdate().isoformat(),
                "hosting_next_income_date": next_income_date.isoformat(),
                "hosting_end_date": end_date.isoformat(),
                "hosting_comment": "Ежемесячный хостинг",
            },
        )

        order.refresh_from_db()
        subscription = HostingSubscription.objects.get(order=order)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(subscription.monthly_amount, Decimal("750.00"))
        self.assertEqual(subscription.next_income_date, next_income_date)
        self.assertEqual(subscription.end_date, end_date)
        self.assertTrue(subscription.is_active)
        self.assertEqual(order.next_payment_date, next_income_date)
        self.assertEqual(order.subscription_end_date, end_date)
