from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from portfolio.models import Project, ProjectImage


class DashboardViewTests(TestCase):
    def test_dashboard_redirects_to_crm_registry(self):
        user = get_user_model().objects.create_user(
            username="manager",
            password="test-pass-123",
            is_staff=True,
        )

        self.client.force_login(user)
        response = self.client.get(reverse("dashboard"))

        self.assertRedirects(response, reverse("crm_order_list"))

    def test_old_registries_url_is_not_available(self):
        user = get_user_model().objects.create_user(
            username="manager2",
            password="test-pass-123",
            is_staff=True,
        )

        self.client.force_login(user)
        response = self.client.get("/dashboard/registries/")

        self.assertEqual(response.status_code, 404)


class HomeViewTests(TestCase):
    def test_client_alias_renders_homepage(self):
        response = self.client.get(reverse("client"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/home.html")

    def test_homepage_shows_up_to_nine_published_projects(self):
        start_date = date(2026, 1, 1)
        for index in range(10):
            Project.objects.create(
                title=f"Project {index}",
                short_description="Short description",
                description="Long description",
                completion_date=start_date + timedelta(days=index),
                stack_notes="HTML, CSS",
                is_published=True,
                is_featured=index == 9,
            )
        hidden_project = Project.objects.create(
            title="Hidden project",
            short_description="Short description",
            description="Long description",
            completion_date=start_date + timedelta(days=30),
            stack_notes="HTML, CSS",
            is_published=False,
        )

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        projects = list(response.context["featured_projects"])
        self.assertEqual(len(projects), 9)
        self.assertTrue(any(not project.is_featured for project in projects))
        self.assertNotIn(hidden_project, projects)

    def test_homepage_uses_portfolio_slider_cards_block(self):
        project = Project.objects.create(
            title="Project slider",
            short_description="Short description",
            description="Long description",
            completion_date=date(2026, 2, 1),
            stack_notes="HTML, CSS",
            color_palette="#14344C, #C96F3B, #F4F1EA, #2B506B",
            cover_image="portfolio/covers/autoparts-catalog.jpg",
            is_published=True,
            is_featured=True,
        )
        ProjectImage.objects.create(
            project=project,
            image="portfolio/gallery/aesthetics-house-gallery-1.jpg",
            caption="Gallery image",
            order=1,
        )

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Примеры наших работ")
        self.assertContains(response, "portfolio-project-grid")
        self.assertContains(response, "data-project-slider")
        self.assertContains(response, project.cover_image.url)

    def test_homepage_passes_six_popular_projects_for_responsive_grid(self):
        start_date = date(2026, 3, 1)
        for index in range(7):
            Project.objects.create(
                title=f"Popular project {index}",
                short_description="Short description",
                description="Long description",
                completion_date=start_date + timedelta(days=index),
                stack_notes="HTML, CSS",
                is_published=True,
            )

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["popular_projects"]), 6)
        self.assertContains(response, "home-portfolio-grid")

    def test_homepage_shows_complex_project_section(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "gas-spec.ru")
        self.assertContains(response, "180к")
        self.assertContains(response, "Подробнее")
        self.assertContains(response, "Написать")
        self.assertContains(response, "complexCaseDetails")
        self.assertContains(response, "WebDAV")
        self.assertContains(response, "1 января 2026 года")
        self.assertNotContains(response, "Lorem ipsum")

    def test_homepage_shows_bundle_services_section(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Обычно берут вместе")
        self.assertContains(response, "Написание сайта")
        self.assertContains(response, "Хостинг сайта")
        self.assertContains(response, "Регистрация домена")
        self.assertContains(response, "Акция -25%")
        self.assertContains(response, "Ещё можно добавить")
        self.assertContains(response, "Создание логотипа")
        self.assertContains(response, "Подробнее")
        self.assertContains(response, "data-home-service-picker")
        self.assertContains(response, "data-home-summary-widget")

    def test_homepage_marks_site_development_as_default_service(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertRegex(content, r'id="home-service-site_development"[^>]*checked')
        self.assertNotRegex(content, r'id="home-service-hosting"[^>]*checked')
        self.assertNotRegex(content, r'id="home-service-domain"[^>]*checked')
