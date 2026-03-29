from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

from core.models import TimeStampedModel
from core.security import decrypt_value, encrypt_value


class Client(TimeStampedModel):
    class ClientType(models.TextChoices):
        INDIVIDUAL = "individual", "Физ. лицо"
        SOLE_PROPRIETOR = "sole_proprietor", "ИП"
        LEGAL_ENTITY = "legal_entity", "Юр. лицо"

    class Status(models.TextChoices):
        NEW = "new", "Новый"
        IN_PROGRESS = "in_progress", "В работе"
        DNS_PENDING = "dns_pending", "Ожидание обновления DNS"
        COMPLETED = "completed", "Выполнено"

    class PreferredContactApp(models.TextChoices):
        PHONE = "phone", "Звонок"
        WHATSAPP = "whatsapp", "WhatsApp"
        TELEGRAM = "telegram", "Telegram"
        EMAIL = "email", "Email"

    name = models.CharField("Контактное лицо", max_length=150)
    company_name = models.CharField("Компания", max_length=150)
    email = models.EmailField("Email")
    phone = models.CharField("Телефон", max_length=50)
    client_type = models.CharField(
        "Тип лица",
        max_length=20,
        choices=ClientType.choices,
        default=ClientType.INDIVIDUAL,
    )
    preferred_contact_app = models.CharField(
        "Предпочитаемый способ связи",
        max_length=20,
        choices=PreferredContactApp.choices,
        default=PreferredContactApp.WHATSAPP,
    )
    telegram = models.CharField("Telegram", max_length=100, blank=True)
    website = models.URLField("Сайт", blank=True)
    notes = models.TextField("Комментарий", blank=True)
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.NEW)

    class Meta:
        ordering = ("company_name", "name")
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self) -> str:
        return self.company_name

    @property
    def is_active(self) -> bool:
        return self.status != self.Status.COMPLETED


class Order(TimeStampedModel):
    class Status(models.TextChoices):
        NEW = "new", "Новый"
        IN_PROGRESS = "in_progress", "В работе"
        DNS_PENDING = "dns_pending", "Ожидание обновления DNS"
        COMPLETED = "completed", "Выполнено"

    class PaymentStatus(models.TextChoices):
        PAID = "paid", "Оплачено"
        PARTIAL = "partial", "Частично оплачено"
        UNPAID = "unpaid", "Не оплачено"
        OVERDUE = "overdue", "Просрочено"

    client = models.ForeignKey(
        Client,
        verbose_name="Клиент",
        related_name="orders",
        on_delete=models.CASCADE,
    )
    brief = models.ForeignKey(
        "briefs.BriefRequest",
        verbose_name="Связанное ТЗ",
        related_name="orders",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    title = models.CharField("Проект / заказ", max_length=200)
    slug = models.SlugField("Слаг", unique=True, blank=True)
    description = models.TextField("Описание", blank=True)
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.NEW)
    start_date = models.DateField("Дата начала")
    end_date = models.DateField("Дата окончания", blank=True, null=True)
    subscription_term_days = models.PositiveIntegerField("Количество дней", blank=True, null=True)
    subscription_term_months = models.PositiveIntegerField("Срок подписки, мес.", blank=True, null=True)
    subscription_end_date = models.DateField("Дата окончания подписки", blank=True, null=True)
    domain = models.CharField("Домен", max_length=255, blank=True)
    domain_expiration_date = models.DateField("Окончание домена", blank=True, null=True)
    server_ip = models.GenericIPAddressField("IP сервера", protocol="both", blank=True, null=True)
    server_username = models.CharField("Пользователь сервера", max_length=150, blank=True)
    server_password_encrypted = models.TextField("Пароль сервера (зашифровано)", blank=True)
    server_expiration_date = models.DateField("Окончание сервера", blank=True, null=True)
    payment_status = models.CharField(
        "Статус оплаты",
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID,
    )
    next_payment_date = models.DateField("Дата следующей оплаты", blank=True, null=True)
    price = models.DecimalField("Стоимость", max_digits=10, decimal_places=2, default=0)
    comments = models.TextField("Комментарии", blank=True)

    class Meta:
        ordering = ("-updated_at",)
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return f"{reverse('crm_client_edit', kwargs={'pk': self.client_id})}?order={self.pk}#order-{self.pk}"

    def clean(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "Дата окончания не может быть раньше даты начала."})
        if self.subscription_end_date and self.subscription_end_date < self.start_date:
            raise ValidationError(
                {"subscription_end_date": "Дата окончания подписки не может быть раньше даты начала."}
            )

    def save(self, *args, **kwargs):
        if self.start_date and self.subscription_term_days:
            calculated_end_date = self.start_date + timedelta(days=self.subscription_term_days - 1)
            self.end_date = calculated_end_date
            if not self.next_payment_date:
                self.subscription_end_date = calculated_end_date
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Order.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        super().save(*args, **kwargs)
        from .services import sync_order_project_income

        sync_order_project_income(self)

    @property
    def has_server_password(self) -> bool:
        return bool(self.server_password_encrypted)

    @property
    def decrypted_server_password(self) -> str:
        return decrypt_value(self.server_password_encrypted)

    def set_server_password(self, raw_password: str):
        self.server_password_encrypted = encrypt_value(raw_password)

    @property
    def is_closed(self) -> bool:
        return self.status == self.Status.COMPLETED


class HostingSubscription(TimeStampedModel):
    order = models.OneToOneField(
        Order,
        verbose_name="Заказ",
        related_name="hosting_subscription",
        on_delete=models.CASCADE,
    )
    monthly_amount = models.DecimalField("Ежемесячный платеж", max_digits=10, decimal_places=2)
    start_date = models.DateField("Дата старта подписки")
    next_income_date = models.DateField("Дата следующего поступления")
    end_date = models.DateField("Дата окончания подписки", blank=True, null=True)
    is_active = models.BooleanField("Подписка активна", default=True)
    comment = models.TextField("Комментарий", blank=True)

    class Meta:
        ordering = ("next_income_date", "pk")
        verbose_name = "Хостинг-подписка"
        verbose_name_plural = "Хостинг-подписки"

    def __str__(self) -> str:
        return f"Хостинг - {self.order.title}"

    @property
    def client(self):
        return self.order.client
