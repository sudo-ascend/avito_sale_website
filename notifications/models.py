from django.db import models

from core.models import TimeStampedModel


class ReminderRule(TimeStampedModel):
    name = models.CharField("Название", max_length=150, blank=True)
    days_before = models.PositiveIntegerField("За сколько дней")
    is_active = models.BooleanField("Активно", default=True)

    class Meta:
        ordering = ("days_before",)
        verbose_name = "Правило напоминания"
        verbose_name_plural = "Правила напоминаний"
        constraints = [
            models.UniqueConstraint(fields=("days_before",), name="unique_days_before_rule"),
        ]

    def __str__(self) -> str:
        return self.name or f"За {self.days_before} дн."

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = f"Напомнить за {self.days_before} дн."
        super().save(*args, **kwargs)


class NotificationLog(TimeStampedModel):
    class EventType(models.TextChoices):
        SUBSCRIPTION = "subscription", "Подписка"
        DOMAIN = "domain", "Домен"
        SERVER = "server", "Сервер"
        DNS_UPDATED = "dns_updated", "DNS обновился"
        HOSTING_INCOME = "hosting_income", "Доход по хостингу"

    class Status(models.TextChoices):
        SENT = "sent", "Отправлено"
        ERROR = "error", "Ошибка"
        SKIPPED = "skipped", "Пропущено"

    reference_key = models.CharField("Ключ уникальности", max_length=255)
    event_type = models.CharField("Тип события", max_length=30, choices=EventType.choices)
    order = models.ForeignKey(
        "crm.Order",
        verbose_name="Заказ",
        related_name="notification_logs",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    dns_target = models.ForeignKey(
        "dns_monitor.DNSMonitorTarget",
        verbose_name="DNS-цель",
        related_name="notification_logs",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    recipient_email = models.EmailField("Получатель")
    target_date = models.DateField("Дата события", blank=True, null=True)
    days_before = models.PositiveIntegerField("Осталось дней", blank=True, null=True)
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.SENT)
    subject = models.CharField("Тема письма", max_length=255)
    message = models.TextField("Текст письма")
    sent_at = models.DateTimeField("Отправлено", auto_now_add=True)

    class Meta:
        ordering = ("-sent_at",)
        verbose_name = "Лог уведомления"
        verbose_name_plural = "Логи уведомлений"
        constraints = [
            models.UniqueConstraint(fields=("reference_key",), name="unique_notification_reference_key"),
        ]

    def __str__(self) -> str:
        return self.subject
