from os.path import basename

from django.core.validators import RegexValidator
from django.db import models
from django.utils.functional import cached_property

from core.models import TimeStampedModel
from .pricing import get_selected_extra_services


def brief_attachment_upload_to(instance, filename):
    return f"briefs/{instance.category}/{filename}"


class BriefRequest(TimeStampedModel):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        IN_REVIEW = "in_review", "В работе"
        PROPOSAL = "proposal", "Подготовлено предложение"
        SIGNED = "signed", "Договор подписан"
        REJECTED = "rejected", "Отклонена"

    class ClientType(models.TextChoices):
        INDIVIDUAL = "individual", "Физ. лицо"
        SOLE_PROPRIETOR = "sole_proprietor", "ИП"
        LEGAL_ENTITY = "legal_entity", "Юр. лицо"

    class SiteType(models.TextChoices):
        SINGLE_PAGE = "single_page", "Одностраничный сайт - визитка / резюме"
        CATALOG = "catalog", "Сайт-каталог"

    class ContactApp(models.TextChoices):
        PHONE = "phone", "Звонок"
        WHATSAPP = "whatsapp", "WhatsApp"
        TELEGRAM = "telegram", "Telegram"
        EMAIL = "email", "Email"

    class HostingPlan(models.TextChoices):
        MONTHLY = "monthly", "1 месяц"
        QUARTERLY = "quarterly", "3 месяца (-25%)"

    class ColorMode(models.TextChoices):
        TEMPLATE = "template", "По шаблону"
        CUSTOM = "custom", "Кастом"

    business_name = models.CharField("Название компании / имя", max_length=150, default="")
    client_type = models.CharField(
        "Тип клиента",
        max_length=20,
        choices=ClientType.choices,
        default=ClientType.INDIVIDUAL,
    )
    site_type = models.CharField(
        "Тип сайта",
        max_length=20,
        choices=SiteType.choices,
        default=SiteType.SINGLE_PAGE,
    )
    photos_file = models.FileField(
        "Фотографии",
        upload_to="briefs/photos/",
        blank=True,
        null=True,
    )
    texts_file = models.FileField(
        "Тексты",
        upload_to="briefs/texts/",
        blank=True,
        null=True,
    )
    reviews_file = models.FileField(
        "Скрины отзывов",
        upload_to="briefs/reviews/",
        blank=True,
        null=True,
    )
    contact_phone = models.CharField("Телефон", max_length=50, default="")
    preferred_contact_app = models.CharField(
        "Предпочитаемое приложение для связи",
        max_length=20,
        choices=ContactApp.choices,
        default=ContactApp.WHATSAPP,
    )
    contact_email = models.EmailField("Email", default="")
    work_region = models.CharField("Адрес / регион работы", max_length=255, default="")
    logo = models.ImageField("Логотип", upload_to="briefs/logos/", blank=True, null=True)
    color_mode = models.CharField(
        "Режим выбора цветов",
        max_length=20,
        choices=ColorMode.choices,
        default=ColorMode.TEMPLATE,
    )
    color_template_name = models.CharField("Выбранный шаблон палитры", max_length=150, blank=True)
    color_preference = models.CharField(
        "Основной цвет",
        max_length=7,
        default="#14344c",
        validators=[RegexValidator(regex=r"^#[0-9A-Fa-f]{6}$", message="Укажите цвет в формате #RRGGBB.")],
    )
    color_accent = models.CharField(
        "Акцентный цвет",
        max_length=7,
        default="#c96f3b",
        validators=[RegexValidator(regex=r"^#[0-9A-Fa-f]{6}$", message="Укажите цвет в формате #RRGGBB.")],
    )
    color_background = models.CharField(
        "Фоновый цвет",
        max_length=7,
        default="#f4f1ea",
        validators=[RegexValidator(regex=r"^#[0-9A-Fa-f]{6}$", message="Укажите цвет в формате #RRGGBB.")],
    )
    color_extra = models.CharField(
        "Дополнительный цвет",
        max_length=7,
        default="#2b506b",
        validators=[RegexValidator(regex=r"^#[0-9A-Fa-f]{6}$", message="Укажите цвет в формате #RRGGBB.")],
    )
    reference_sites = models.TextField("Примеры сайтов", blank=True)
    desired_domain = models.CharField("Желаемый домен", max_length=255, blank=True)
    extra_pages = models.PositiveIntegerField("Количество доп. страниц", default=0)
    need_hosting = models.BooleanField("Добавить хостинг", default=False)
    hosting_plan = models.CharField(
        "Период оплаты хостинга",
        max_length=20,
        choices=HostingPlan.choices,
        default=HostingPlan.MONTHLY,
    )
    need_domain = models.BooleanField("Добавить домен", default=False)
    need_logo_design = models.BooleanField("Создание логотипа", default=False)
    need_basic_seo = models.BooleanField("Базовое SEO продвижение", default=False)
    need_photo_selection = models.BooleanField("Подбор фото и картинок", default=False)
    need_email_form = models.BooleanField("Форма с отправкой писем на почту", default=False)
    need_reviews_section = models.BooleanField("Секция с отзывами", default=False)
    client_comment = models.TextField("Комментарий клиента", blank=True, default="")
    estimated_price = models.DecimalField("Ориентировочная стоимость", max_digits=10, decimal_places=2, default=0)
    privacy_accepted = models.BooleanField("Согласие на обработку данных", default=False)
    manager_comment = models.TextField("Комментарий менеджера", blank=True)
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Заявка / ТЗ"
        verbose_name_plural = "Заявки / ТЗ"

    def __str__(self) -> str:
        return self.business_name

    def get_service_categories_display(self) -> str:
        return self.get_site_type_display()

    @property
    def palette_colors(self) -> list[str]:
        return [self.color_preference, self.color_accent, self.color_background, self.color_extra]

    @property
    def palette_summary(self) -> str:
        return ", ".join(self.palette_colors)

    @property
    def selected_extra_services(self) -> list[str]:
        return get_selected_extra_services(
            extra_pages=self.extra_pages,
            need_hosting=self.need_hosting,
            hosting_plan=self.hosting_plan,
            need_domain=self.need_domain,
            need_logo_design=self.need_logo_design,
            need_basic_seo=self.need_basic_seo,
            need_photo_selection=self.need_photo_selection,
            need_email_form=self.need_email_form,
            need_reviews_section=self.need_reviews_section,
        )

    @property
    def selected_extra_services_summary(self) -> str:
        extras = self.selected_extra_services
        return ", ".join(extras) if extras else "-"

    @cached_property
    def attachments_by_category(self):
        attachments = getattr(self, "_prefetched_objects_cache", {}).get("attachments")
        if attachments is None:
            attachments = self.attachments.all()

        grouped = {
            BriefAttachment.Category.PHOTOS: [],
            BriefAttachment.Category.TEXTS: [],
            BriefAttachment.Category.REVIEWS: [],
        }
        for attachment in attachments:
            grouped.setdefault(attachment.category, []).append(attachment)
        return grouped

    @property
    def photo_attachments(self):
        return self.attachments_by_category.get(BriefAttachment.Category.PHOTOS, [])

    @property
    def text_attachments(self):
        return self.attachments_by_category.get(BriefAttachment.Category.TEXTS, [])

    @property
    def review_attachments(self):
        return self.attachments_by_category.get(BriefAttachment.Category.REVIEWS, [])


class BriefAttachment(TimeStampedModel):
    class Category(models.TextChoices):
        PHOTOS = "photos", "Фотки"
        TEXTS = "texts", "Тексты"
        REVIEWS = "reviews", "Скрины отзывов"

    brief = models.ForeignKey(
        BriefRequest,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Заявка",
    )
    category = models.CharField("Категория", max_length=20, choices=Category.choices)
    file = models.FileField("Файл", upload_to=brief_attachment_upload_to)

    class Meta:
        ordering = ("created_at", "pk")
        verbose_name = "Вложение заявки"
        verbose_name_plural = "Вложения заявок"

    def __str__(self) -> str:
        return f"{self.get_category_display()} - {self.filename}"

    @property
    def filename(self) -> str:
        return basename(self.file.name)
