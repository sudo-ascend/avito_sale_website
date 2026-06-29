from datetime import date

from django.test import TestCase
from django.urls import reverse

from portfolio.models import Project, ProjectImage


class HomeViewTests(TestCase):
    def test_client_alias_renders_homepage(self):
        response = self.client.get(reverse("client"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/home.html")

    def test_homepage_header_shows_public_navigation(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("home"))
        self.assertContains(response, reverse("portfolio_list"))
        self.assertContains(response, reverse("brief_create"))
        self.assertContains(response, reverse("contact"))
        self.assertNotContains(response, "CRM")
        self.assertNotContains(response, "Telegram-боты")

    def test_homepage_shows_first_six_projects_from_catalog_order(self):
        for index in range(8):
            Project.objects.create(
                title=f"Project {index}",
                short_description="Short description",
                description="Long description",
                completion_date=date(2026, 1, index + 1),
                stack_notes="HTML, CSS",
                is_published=True,
                catalog_order=index + 1,
            )

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        projects = list(response.context["popular_projects"])
        self.assertEqual(len(projects), 6)
        self.assertEqual([project.catalog_order for project in projects], [1, 2, 3, 4, 5, 6])

    def test_homepage_renders_aquaklon_case_section_and_placeholders(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aquaklon.ru")
        self.assertContains(response, "Место для изображения 16:9")

    def test_homepage_service_picker_keeps_summary_widget(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data-home-service-picker")
        self.assertContains(response, "data-home-summary-widget")
        self.assertContains(response, "Админ панель для смены текстов сайта")
        self.assertContains(response, "Админ панель для редактирования каталога товаров")

    def test_homepage_project_cards_use_cover_and_gallery_images(self):
        project = Project.objects.create(
            title="Project slider",
            short_description="Short description",
            description="Long description",
            completion_date=date(2026, 2, 1),
            stack_notes="HTML, CSS",
            color_palette="#14344C, #C96F3B, #F4F1EA, #2B506B",
            cover_image="portfolio/covers/autoparts-catalog.jpg",
            cover_image_alt="Обложка проекта",
            is_published=True,
            catalog_order=1,
        )
        ProjectImage.objects.create(
            project=project,
            image="portfolio/gallery/aesthetics-house-gallery-1.jpg",
            caption="Gallery image",
            alt_text="Gallery alt",
            order=1,
        )

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, project.cover_image.url)
        self.assertContains(response, "Обложка проекта")
        self.assertContains(response, "Gallery alt")


class SiteTypeGuideViewTests(TestCase):
    def test_site_type_guide_is_available(self):
        response = self.client.get(reverse("site_type_guide"))

        self.assertEqual(response.status_code, 200)


class ContactViewTests(TestCase):
    def test_contact_page_shows_fallback_contact_details(self):
        response = self.client.get(reverse("contact"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/contact.html")
        self.assertContains(response, "grachevilia09@yandex.ru")
        self.assertContains(response, "79167950225")
