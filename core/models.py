from django.db import models
from django.urls import reverse


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        abstract = True


class Service(TimeStampedModel):
    title = models.CharField("Название", max_length=150)
    slug = models.SlugField("Слаг", unique=True)
    icon = models.CharField(
        "Иконка Bootstrap",
        max_length=100,
        default="bi-layers",
        help_text="Например: bi-globe2, bi-window, bi-phone.",
    )
    short_description = models.CharField("Краткое описание", max_length=255)
    description = models.TextField("Подробное описание")
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активно", default=True)

    class Meta:
        ordering = ("order", "title")
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("home")


class HomePageCaseSection(TimeStampedModel):
    kicker = models.CharField("Кикер секции", max_length=120, default="Опыт с админкой")
    title = models.CharField("Заголовок", max_length=255)
    body = models.TextField("Текст секции")
    image_primary = models.ImageField("Первая картинка", upload_to="home/case/", blank=True, null=True)
    image_primary_alt = models.CharField("Alt первой картинки", max_length=255, blank=True)
    image_secondary = models.ImageField("Вторая картинка", upload_to="home/case/", blank=True, null=True)
    image_secondary_alt = models.CharField("Alt второй картинки", max_length=255, blank=True)
    is_active = models.BooleanField("Показывать на главной", default=True)

    class Meta:
        verbose_name = "Секция кейса на главной"
        verbose_name_plural = "Секция кейса на главной"

    def __str__(self) -> str:
        return self.title


class ContactInfo(TimeStampedModel):
    company_name = models.CharField("Название компании", max_length=150)
    tagline = models.CharField("Подзаголовок", max_length=255, blank=True)
    email = models.EmailField("Email")
    phone = models.CharField("Телефон", max_length=50)
    telegram = models.CharField("Telegram", max_length=100, blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=100, blank=True)
    address = models.CharField("Адрес", max_length=255, blank=True)
    working_hours = models.CharField("Часы работы", max_length=150, blank=True)
    map_embed_url = models.URLField("Ссылка на карту", blank=True)
    is_primary = models.BooleanField("Основной контакт", default=True)

    class Meta:
        verbose_name = "Контактная информация"
        verbose_name_plural = "Контактная информация"

    def __str__(self) -> str:
        return self.company_name
