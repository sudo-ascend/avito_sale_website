from django.db import models

from core.models import TimeStampedModel


class DNSMonitorTarget(TimeStampedModel):
    class RecordType(models.TextChoices):
        A = "A", "A"
        AAAA = "AAAA", "AAAA"
        CNAME = "CNAME", "CNAME"
        TXT = "TXT", "TXT"

    class Status(models.TextChoices):
        UNKNOWN = "unknown", "Не проверялось"
        UPDATED = "updated", "Обновился"
        NOT_UPDATED = "not_updated", "Не обновился"
        ERROR = "error", "Ошибка"

    order = models.ForeignKey(
        "crm.Order",
        verbose_name="Заказ",
        related_name="dns_targets",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    domain = models.CharField("Домен", max_length=255)
    record_type = models.CharField("Тип записи", max_length=10, choices=RecordType.choices, default=RecordType.A)
    expected_value = models.CharField("Ожидаемое значение", max_length=255)
    is_active = models.BooleanField("Активен", default=True)
    last_status = models.CharField(
        "Последний статус",
        max_length=20,
        choices=Status.choices,
        default=Status.UNKNOWN,
    )
    last_checked_at = models.DateTimeField("Последняя проверка", blank=True, null=True)
    last_resolved_value = models.TextField("Последнее полученное значение", blank=True)
    last_message = models.TextField("Последнее сообщение", blank=True)
    last_success_notification_at = models.DateTimeField(
        "Последнее уведомление об обновлении",
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ("domain",)
        verbose_name = "DNS-цель"
        verbose_name_plural = "DNS-цели"

    def __str__(self) -> str:
        return f"{self.domain} ({self.record_type})"

    def save(self, *args, **kwargs):
        if self.order:
            self.domain = self.domain or self.order.domain
            if not self.expected_value and self.order.server_ip and self.record_type == self.RecordType.A:
                self.expected_value = self.order.server_ip
        super().save(*args, **kwargs)


class DNSCheckLog(TimeStampedModel):
    target = models.ForeignKey(
        DNSMonitorTarget,
        verbose_name="Цель",
        related_name="logs",
        on_delete=models.CASCADE,
    )
    checked_at = models.DateTimeField("Проверено", auto_now_add=True)
    status = models.CharField("Статус", max_length=20, choices=DNSMonitorTarget.Status.choices)
    resolved_value = models.TextField("Полученное значение", blank=True)
    message = models.TextField("Сообщение", blank=True)
    response_payload = models.JSONField("Сырой ответ", blank=True, default=list)

    class Meta:
        ordering = ("-checked_at",)
        verbose_name = "Лог DNS-проверки"
        verbose_name_plural = "Логи DNS-проверок"

    def __str__(self) -> str:
        return f"{self.target.domain} - {self.get_status_display()}"
