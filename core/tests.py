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

    def test_homepage_header_shows_logo_and_primary_nav(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="site-brand"')
        self.assertContains(response, reverse("home"))
        self.assertContains(response, reverse("portfolio_list"))
        self.assertContains(response, reverse("brief_create"))
        self.assertContains(response, reverse("contact"))
        self.assertContains(response, "Составить ТЗ")
        self.assertNotContains(response, 'href="/#services"')

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
        self.assertContains(response, "/static/img/home/gas-system-presentation-shot.png")
        self.assertContains(response, "/static/img/home/gas-system-presentation-order-edit.png")
        self.assertContains(response, "ООО «Специалист»")
        self.assertContains(response, "Готовые решения оказались слишком сложными")
        self.assertContains(response, "Что сделано")
        self.assertContains(response, "Реестры заказов, договоров и проектов")
        self.assertNotContains(response, "180к")
        self.assertContains(response, "Написать")
        self.assertContains(response, "WebDAV")
        self.assertNotContains(response, 'data-bs-target="#complexCaseDetails"')
        self.assertNotContains(response, "Lorem ipsum")

    def test_homepage_does_not_show_removed_advantages(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Проще масштабировать")
        self.assertNotContains(response, "Без лишнего мусора")
        self.assertNotContains(response, "Понятное сопровождение")
        self.assertNotContains(response, "После запуска можно быстро вносить правки")
        self.assertNotContains(response, "Масштабирование")
        self.assertNotContains(response, "Понятный процесс без хаоса")

    def test_homepage_shows_contacts_in_footer(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="contacts"')
        self.assertContains(response, "footer-contact-list")
        self.assertContains(response, "Почта")
        self.assertContains(response, "Телефон")
        self.assertContains(response, "grachevilia09@yandex.ru")
        self.assertContains(response, "79167950225")
        self.assertContains(response, "footer-credit")
        self.assertContains(response, "btn-brand")
        self.assertNotContains(response, "contact-shell")
        self.assertNotContains(response, "Заполните email в админке")
        self.assertNotContains(response, "Добавьте номер телефона")
        self.assertNotContains(response, "Выберите удобный способ связи")

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
        self.assertContains(response, "Telegram-боты и связка с сайтом")

    def test_homepage_shows_telegram_bot_block_under_business_systems(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="telegram-bots"')
        self.assertContains(response, "Идеи для Telegram-бота: зачем он нужен и как работает")
        self.assertContains(response, "Зачем")
        self.assertContains(response, "Как")
        self.assertContains(response, "Подходит как отдельная услуга или как дополнение к сайту")
        self.assertContains(response, "telegram-bot-chat-menu.jpg")
        self.assertContains(response, "telegram-bot-chat-invoice.jpg")

    def test_homepage_leaves_bundle_services_unselected_by_default(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertNotRegex(content, r'id="home-service-site_development"[^>]*checked')
        self.assertNotRegex(content, r'id="home-service-hosting"[^>]*checked')
        self.assertNotRegex(content, r'id="home-service-domain"[^>]*checked')
        self.assertRegex(
            content,
            r'<aside class="brief-price-widget brief-price-widget--idle card border-0 shadow-sm" data-home-summary-widget>',
        )
        self.assertContains(response, "Положите в корзину")
        self.assertContains(response, "data-home-summary-empty-close")


class SiteTypeGuideViewTests(TestCase):
    def test_site_type_guide_avoids_removed_scaling_phrase(self):
        response = self.client.get(reverse("site_type_guide"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "лучше масштабируется, когда бизнес растёт")


class ContactViewTests(TestCase):
    def test_contact_page_shows_fallback_contact_details(self):
        response = self.client.get(reverse("contact"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/contact.html")
        self.assertContains(response, "grachevilia09@yandex.ru")
        self.assertContains(response, "79167950225")
        self.assertNotContains(response, "Контактные данные пока не заполнены")
