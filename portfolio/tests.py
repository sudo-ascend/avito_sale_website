import tempfile
from pathlib import Path

from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Project


@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
class PortfolioDemoPageTests(TestCase):
    def setUp(self):
        super().setUp()
        self.media_root = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_root.name)
        self.settings_override.enable()
        self.project = Project.objects.create(
            title="Demo Project",
            short_description="Короткое описание",
            description="Полное описание проекта",
            completion_date="2026-03-29",
            stack_notes="HTML, CSS",
            external_url="https://example.com",
            is_published=True,
        )
        site_dir = Path(self.media_root.name) / "portfolio" / "sites" / self.project.slug
        site_dir.mkdir(parents=True, exist_ok=True)
        (site_dir / "index.html").write_text("<html><body>Demo site</body></html>", encoding="utf-8")

    def tearDown(self):
        self.settings_override.disable()
        self.media_root.cleanup()
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
