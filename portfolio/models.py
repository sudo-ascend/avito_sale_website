from pathlib import Path

from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

from core.models import TimeStampedModel


class Project(TimeStampedModel):
    title = models.CharField("Название", max_length=200)
    slug = models.SlugField("Слаг", unique=True, blank=True)
    short_description = models.CharField("Краткое описание", max_length=255)
    description = models.TextField("Описание")
    completion_date = models.DateField("Дата проекта")
    stack_notes = models.CharField("Кратко о стеке", max_length=255, blank=True)
    external_url = models.URLField("Ссылка", blank=True)
    cover_image = models.ImageField("Обложка", upload_to="portfolio/covers/", blank=True, null=True)
    cover_image_alt = models.CharField("Alt обложки", max_length=255, blank=True)
    color_palette = models.CharField("Палитра проекта", max_length=255, blank=True)
    catalog_order = models.PositiveIntegerField("Порядок в каталоге", default=0)
    is_featured = models.BooleanField("Показывать на главной", default=False)
    is_published = models.BooleanField("Опубликован", default=True)

    class Meta:
        ordering = ("catalog_order", "-completion_date", "-created_at")
        verbose_name = "Проект портфолио"
        verbose_name_plural = "Проекты портфолио"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Project.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        if not self.cover_image_alt:
            self.cover_image_alt = self.title
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("portfolio_detail", kwargs={"slug": self.slug})

    @property
    def demo_site_path(self) -> Path:
        return Path(settings.MEDIA_ROOT) / "portfolio" / "sites" / self.slug / "index.html"

    @property
    def has_demo_site(self) -> bool:
        return self.demo_site_path.exists()

    @property
    def demo_url(self) -> str:
        return reverse("portfolio_site", kwargs={"slug": self.slug})

    @property
    def palette_colors(self) -> list[str]:
        if self.color_palette:
            colors = [item.strip() for item in self.color_palette.split(",") if item.strip()]
            if colors:
                return colors
        return []


class ProjectImage(TimeStampedModel):
    project = models.ForeignKey(
        Project,
        verbose_name="Проект",
        related_name="images",
        on_delete=models.CASCADE,
    )
    image = models.ImageField("Изображение", upload_to="portfolio/gallery/")
    caption = models.CharField("Подпись", max_length=255, blank=True)
    alt_text = models.CharField("Alt изображения", max_length=255, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        ordering = ("order", "pk")
        verbose_name = "Изображение проекта"
        verbose_name_plural = "Изображения проектов"

    def __str__(self) -> str:
        return f"{self.project.title} #{self.order}"

    def save(self, *args, **kwargs):
        if not self.alt_text:
            self.alt_text = self.caption or self.project.title
        super().save(*args, **kwargs)
