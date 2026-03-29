from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

from core.models import TimeStampedModel


class Technology(TimeStampedModel):
    name = models.CharField("Название", max_length=100, unique=True)
    slug = models.SlugField("Слаг", unique=True, blank=True)
    color = models.CharField("Цвет", max_length=7, default="#14344C")

    class Meta:
        ordering = ("name",)
        verbose_name = "Технология"
        verbose_name_plural = "Технологии"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Project(TimeStampedModel):
    title = models.CharField("Название", max_length=200)
    slug = models.SlugField("Слаг", unique=True, blank=True)
    short_description = models.CharField("Краткое описание", max_length=255)
    description = models.TextField("Описание")
    completion_date = models.DateField("Дата проекта")
    stack_notes = models.CharField("Кратко о стеке", max_length=255, blank=True)
    external_url = models.URLField("Ссылка", blank=True)
    cover_image = models.ImageField("Обложка", upload_to="portfolio/covers/", blank=True, null=True)
    color_palette = models.CharField("Палитра проекта", max_length=255, blank=True)
    technologies = models.ManyToManyField(
        Technology,
        verbose_name="Технологии",
        blank=True,
        related_name="projects",
    )
    is_featured = models.BooleanField("Показывать на главной", default=False)
    is_published = models.BooleanField("Опубликован", default=True)

    class Meta:
        ordering = ("-completion_date", "-created_at")
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
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("portfolio_detail", kwargs={"slug": self.slug})

    @property
    def palette_colors(self) -> list[str]:
        if self.color_palette:
            colors = [item.strip() for item in self.color_palette.split(",") if item.strip()]
            if colors:
                return colors
        technology_colors = [technology.color for technology in self.technologies.all()[:4] if technology.color]
        return technology_colors


class ProjectImage(TimeStampedModel):
    project = models.ForeignKey(
        Project,
        verbose_name="Проект",
        related_name="images",
        on_delete=models.CASCADE,
    )
    image = models.ImageField("Изображение", upload_to="portfolio/gallery/")
    caption = models.CharField("Подпись", max_length=255, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        ordering = ("order", "pk")
        verbose_name = "Изображение проекта"
        verbose_name_plural = "Изображения проектов"

    def __str__(self) -> str:
        return f"{self.project.title} #{self.order}"
