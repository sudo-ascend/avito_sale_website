import tempfile
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.datastructures import MultiValueDict

from crm.models import Client as CRMClient, Order

from .forms import BriefRequestForm
from .models import BriefAttachment, BriefRequest


SMALL_GIF = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
    b"\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00"
    b"\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
class BriefRequestFormTests(TestCase):
    def setUp(self):
        super().setUp()
        self.media_root = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_root.name)
        self.settings_override.enable()

    def tearDown(self):
        self.settings_override.disable()
        self.media_root.cleanup()
        super().tearDown()

    def build_form(self, *, files=None, **data):
        default_data = {
            "client_type": BriefRequest.ClientType.INDIVIDUAL,
            "business_name": "Иван Иванов",
            "work_region": "Москва",
            "site_type": BriefRequest.SiteType.SINGLE_PAGE,
            "extra_pages": "0",
            "color_mode": BriefRequest.ColorMode.TEMPLATE,
            "color_template_name": "Template A",
            "color_preference": "#14344c",
            "color_accent": "#c96f3b",
            "color_background": "#f4f1ea",
            "color_extra": "#2b506b",
            "reference_sites": "https://example.com",
            "desired_domain": "example.ru",
            "hosting_plan": BriefRequest.HostingPlan.MONTHLY,
            "contact_phone": "9991234567",
            "preferred_contact_app": "",
            "contact_email": "",
            "client_comment": "",
            "privacy_accepted": "on",
        }
        default_data.update(data)

        default_files = MultiValueDict(
            {
                "photos_files": [
                    SimpleUploadedFile("photo-1.txt", b"photo-1", content_type="text/plain"),
                    SimpleUploadedFile("photo-2.txt", b"photo-2", content_type="text/plain"),
                ],
                "texts_files": [
                    SimpleUploadedFile("text-1.txt", b"text-1", content_type="text/plain"),
                    SimpleUploadedFile("text-2.txt", b"text-2", content_type="text/plain"),
                ],
                "reviews_files": [
                    SimpleUploadedFile("review-1.txt", b"review-1", content_type="text/plain"),
                ],
                "logo": [
                    SimpleUploadedFile("logo.gif", SMALL_GIF, content_type="image/gif"),
                ],
            }
        )
        if files is not None:
            default_files = files

        return BriefRequestForm(data=default_data, files=default_files)

    def test_form_saves_multiple_files_and_optional_contact_fields(self):
        form = self.build_form()

        self.assertTrue(form.is_valid(), form.errors)
        brief = form.save()

        self.assertEqual(brief.contact_email, "")
        self.assertEqual(brief.client_comment, "")
        self.assertEqual(brief.desired_domain, "example.ru")
        self.assertEqual(brief.extra_pages, 0)
        self.assertEqual(brief.preferred_contact_app, BriefRequest.ContactApp.WHATSAPP)
        self.assertEqual(brief.attachments.count(), 5)
        self.assertEqual(
            brief.attachments.filter(category=BriefAttachment.Category.PHOTOS).count(),
            2,
        )
        self.assertEqual(
            brief.attachments.filter(category=BriefAttachment.Category.TEXTS).count(),
            2,
        )
        self.assertEqual(
            brief.attachments.filter(category=BriefAttachment.Category.REVIEWS).count(),
            1,
        )

    def test_reference_sites_is_optional(self):
        form = self.build_form(reference_sites="")

        self.assertTrue(form.is_valid(), form.errors)

    def test_form_calculates_price_for_extra_services_and_discounted_hosting(self):
        form = self.build_form(
            site_type=BriefRequest.SiteType.CATALOG,
            extra_pages="2",
            need_hosting="on",
            hosting_plan=BriefRequest.HostingPlan.QUARTERLY,
            need_domain="on",
            need_logo_design="on",
            need_basic_seo="on",
            need_photo_selection="on",
            need_email_form="on",
            need_reviews_section="on",
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["estimated_price"], Decimal("12987.50"))

        brief = form.save()
        self.assertEqual(
            brief.selected_extra_services,
            [
                "Доп. страницы: 2 x 1 000 ₽",
                "Хостинг сайта на 3 месяца 1 687,50 ₽ (-25%)",
                "Регистрация домена 550 ₽",
                "Создание логотипа 500 ₽",
                "Базовое SEO продвижение 500 ₽",
                "Подбор фото и картинок 2 000 ₽",
                "Форма с отправкой писем на почту 1 500 ₽",
                "Секция с отзывами 250 ₽",
            ],
        )

    def test_form_requires_at_least_one_file_in_required_multiple_groups_only(self):
        files = MultiValueDict(
            {
                "reviews_files": [
                    SimpleUploadedFile("review-1.txt", b"review-1", content_type="text/plain"),
                ],
            }
        )
        form = self.build_form(files=files)

        self.assertFalse(form.is_valid())
        self.assertIn("photos_files", form.errors)
        self.assertIn("texts_files", form.errors)
        self.assertNotIn("reviews_files", form.errors)
        self.assertNotIn("logo", form.errors)

    def test_brief_create_view_accepts_empty_reference_sites_and_syncs_to_crm(self):
        response = self.client.post(
            reverse("brief_create"),
            data={
                "client_type": BriefRequest.ClientType.INDIVIDUAL,
                "business_name": "Иван Иванов",
                "work_region": "Москва",
                "site_type": BriefRequest.SiteType.SINGLE_PAGE,
                "extra_pages": "1",
                "color_mode": BriefRequest.ColorMode.TEMPLATE,
                "color_template_name": "Template A",
                "color_preference": "#14344c",
                "color_accent": "#c96f3b",
                "color_background": "#f4f1ea",
                "color_extra": "#2b506b",
                "reference_sites": "",
                "desired_domain": "site.ru",
                "need_hosting": "on",
                "hosting_plan": BriefRequest.HostingPlan.QUARTERLY,
                "need_logo_design": "on",
                "contact_phone": "9991234567",
                "preferred_contact_app": "",
                "contact_email": "",
                "client_comment": "",
                "privacy_accepted": "on",
                "photos_files": [
                    SimpleUploadedFile("photo-1.txt", b"photo-1", content_type="text/plain"),
                ],
                "texts_files": [
                    SimpleUploadedFile("text-1.txt", b"text-1", content_type="text/plain"),
                ],
                "reviews_files": [
                    SimpleUploadedFile("review-1.txt", b"review-1", content_type="text/plain"),
                ],
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("brief_success"))
        self.assertEqual(BriefRequest.objects.count(), 1)
        self.assertEqual(CRMClient.objects.count(), 1)
        self.assertEqual(Order.objects.count(), 1)

        crm_client = CRMClient.objects.get()
        order = Order.objects.get()
        self.assertEqual(crm_client.status, CRMClient.Status.NEW)
        self.assertEqual(order.status, Order.Status.NEW)
        self.assertEqual(order.client_id, crm_client.pk)
        self.assertIn("Доп. страниц:", order.description)
        self.assertIn("1", order.description)
        self.assertIn("Хостинг сайта на 3 месяца 1 687,50 ₽ (-25%)", order.description)
        self.assertIn("Создание логотипа 500 ₽", order.description)
        self.assertIn("Желаемый домен:", order.description)
        self.assertIn("site.ru", order.description)

    def test_brief_create_view_prefills_selected_services_from_query_params(self):
        response = self.client.get(
            reverse("brief_create"),
            {
                "site_type": BriefRequest.SiteType.CATALOG,
                "extra_pages": "2",
                "need_hosting": "1",
                "hosting_plan": BriefRequest.HostingPlan.QUARTERLY,
                "need_domain": "1",
                "need_logo_design": "1",
            },
        )

        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form["site_type"].value(), BriefRequest.SiteType.CATALOG)
        self.assertEqual(form["extra_pages"].value(), 2)
        self.assertTrue(form["need_hosting"].value())
        self.assertEqual(form["hosting_plan"].value(), BriefRequest.HostingPlan.QUARTERLY)
        self.assertTrue(form["need_domain"].value())
        self.assertTrue(form["need_logo_design"].value())

    def test_brief_create_view_defaults_to_single_page_only(self):
        response = self.client.get(reverse("brief_create"))

        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form["site_type"].value(), BriefRequest.SiteType.SINGLE_PAGE)
        self.assertEqual(form["extra_pages"].value(), 0)
        self.assertFalse(form["need_hosting"].value())
        self.assertFalse(form["need_domain"].value())
        self.assertFalse(form["need_logo_design"].value())
        self.assertFalse(form["need_basic_seo"].value())
        self.assertFalse(form["need_photo_selection"].value())
        self.assertFalse(form["need_email_form"].value())
        self.assertFalse(form["need_reviews_section"].value())
        self.assertTrue(response.context["reset_service_defaults"])
