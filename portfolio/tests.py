import shutil
from pathlib import Path

from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Project, ProjectImage


@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
class PortfolioDemoPageTests(TestCase):
    def setUp(self):
        super().setUp()
        self.media_root = Path(__file__).resolve().parents[1] / "media"
        self.settings_override = override_settings(MEDIA_ROOT=self.media_root)
        self.settings_override.enable()
        self.project = Project.objects.create(
            title="Demo Project",
            short_description="Короткое описание",
            description="Полное описание проекта",
            completion_date="2026-03-29",
            stack_notes="HTML, CSS",
            external_url="https://example.com",
            cover_image="portfolio/covers/autoparts-catalog.jpg",
            color_palette="#14344C, #C96F3B, #F4F1EA, #2B506B",
            is_published=True,
        )
        self.gallery_image = ProjectImage.objects.create(
            project=self.project,
            image="portfolio/gallery/aesthetics-house-gallery-1.jpg",
            caption="Экран проекта",
            order=1,
        )
        self.site_dir = self.media_root / "portfolio" / "sites" / self.project.slug
        self.site_dir.mkdir(parents=True, exist_ok=True)
        (self.site_dir / "index.html").write_text("<html><body>Demo site</body></html>", encoding="utf-8")

    def tearDown(self):
        self.settings_override.disable()
        shutil.rmtree(self.site_dir, ignore_errors=True)
        super().tearDown()

    def test_project_detail_renders_demo_shell_with_iframe(self):
        response = self.client.get(reverse("portfolio_detail", args=[self.project.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ДЕМО режим")
        self.assertContains(response, reverse("portfolio_site", args=[self.project.slug]))
        self.assertContains(response, "iframe")

    def test_portfolio_site_serves_static_index(self):
        response = self.client.get(reverse("portfolio_site", args=[self.project.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Demo site")

    def test_project_list_renders_slider_palette_and_two_column_cards(self):
        response = self.client.get(reverse("portfolio_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "portfolio-project-grid")
        self.assertContains(response, 'class="col-md-6"', html=False)
        self.assertContains(response, "data-project-slider")
        self.assertContains(response, "data-slider-next")
        self.assertContains(response, self.project.cover_image.url)
        self.assertContains(response, self.gallery_image.image.url)
        self.assertContains(response, "Цветовая гамма")
