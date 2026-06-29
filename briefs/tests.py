import tempfile
from decimal import Decimal

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.datastructures import MultiValueDict

from portfolio.models import Project

from .forms import BriefRequestForm
from .models import BriefAttachment, BriefRequest
from .services import get_brief_notification_recipient


SMALL_GIF = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
    b"\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00"
    b"\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


@override_settings(
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    BRIEF_NOTIFICATION_EMAIL="owner@example.com",
)
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

    def test_form_requires_only_reviews_files_from_repeatable_groups(self):
        files = MultiValueDict(
            {
                "reviews_files": [
                    SimpleUploadedFile("review-1.txt", b"review-1", content_type="text/plain"),
                ],
            }
        )
        form = self.build_form(files=files)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertNotIn("reviews_files", form.errors)
        self.assertNotIn("logo", form.errors)

    def test_brief_create_view_accepts_empty_reference_sites_and_sends_email(self):
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
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["owner@example.com"])
        self.assertIn("Заявка в админке", mail.outbox[0].body)
        self.assertNotIn("CRM", mail.outbox[0].body)

        attachment = mail.outbox[0].attachments[0]
        attachment_name = getattr(attachment, "filename", attachment[0])
        attachment_content = getattr(attachment, "content", attachment[1])
        attachment_mimetype = getattr(attachment, "mimetype", attachment[2])
        self.assertTrue(attachment_name.endswith(".pdf"))
        self.assertEqual(attachment_mimetype, "application/pdf")
        self.assertTrue(attachment_content.startswith(b"%PDF"))

    @override_settings(
        BRIEF_NOTIFICATION_EMAIL="grachevilia09",
        DEFAULT_FROM_EMAIL="grachevilia09@yandex.ru",
        NOTIFICATION_EMAIL="owner@example.com",
    )
    def test_brief_notification_recipient_uses_sender_domain_for_login_only_value(self):
        self.assertEqual(get_brief_notification_recipient(), "grachevilia09@yandex.ru")

    def test_brief_success_page_offers_pdf_actions_and_download(self):
        response = self.client.post(
            reverse("brief_create"),
            data={
                "client_type": BriefRequest.ClientType.INDIVIDUAL,
                "business_name": "Тестовый клиент",
                "work_region": "Москва",
                "site_type": BriefRequest.SiteType.SINGLE_PAGE,
                "extra_pages": "0",
                "color_mode": BriefRequest.ColorMode.TEMPLATE,
                "color_template_name": "Template A",
                "color_preference": "#14344c",
                "color_accent": "#c96f3b",
                "color_background": "#f4f1ea",
                "color_extra": "#2b506b",
                "reference_sites": "",
                "desired_domain": "",
                "hosting_plan": BriefRequest.HostingPlan.MONTHLY,
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
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "УСПЕШНО")
        self.assertContains(response, "Сохранить ТЗ у себя")
        self.assertContains(response, "Скачать PDF")

        pdf_response = self.client.get(reverse("brief_download_pdf"))
        self.assertEqual(pdf_response.status_code, 200)
        self.assertEqual(pdf_response["Content-Type"], "application/pdf")
        self.assertIn("attachment;", pdf_response["Content-Disposition"])
        self.assertTrue(pdf_response.content.startswith(b"%PDF"))

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

    def test_brief_create_view_shows_all_published_portfolio_examples(self):
        first_project = Project.objects.create(
            title="First Example",
            short_description="Описание первого проекта",
            description="Полное описание",
            completion_date="2026-03-01",
            stack_notes="HTML, CSS",
            is_published=True,
            is_featured=False,
            catalog_order=2,
        )
        second_project = Project.objects.create(
            title="Second Example",
            short_description="Описание второго проекта",
            description="Полное описание",
            completion_date="2026-03-02",
            stack_notes="HTML, CSS",
            is_published=True,
            is_featured=True,
            catalog_order=1,
        )
        hidden_project = Project.objects.create(
            title="Hidden Example",
            short_description="Скрытый проект",
            description="Полное описание",
            completion_date="2026-03-03",
            stack_notes="HTML, CSS",
            is_published=False,
            catalog_order=3,
        )

        response = self.client.get(reverse("brief_create"))

        self.assertEqual(response.status_code, 200)
        examples = response.context["brief_project_examples"]
        titles = [example["title"] for example in examples]
        self.assertEqual(titles[:2], [second_project.title, first_project.title])
        self.assertNotIn(hidden_project.title, titles)
