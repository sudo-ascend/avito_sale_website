from django.core.validators import MinValueValidator
from django.db import models

from core.models import TimeStampedModel


class AccountingEntry(TimeStampedModel):
    class OperationType(models.TextChoices):
        INCOME = "income", "Доход"
        EXPENSE = "expense", "Расход"

    class Source(models.TextChoices):
        MANUAL = "manual", "Ручная"
        PROJECT_PAYMENT = "project_payment", "Оплата проекта"
        HOSTING_SUBSCRIPTION = "hosting_subscription", "Подписка на хостинг"

    date = models.DateField("Дата")
    operation_type = models.CharField("Тип операции", max_length=20, choices=OperationType.choices)
    source = models.CharField("Источник", max_length=30, choices=Source.choices, default=Source.MANUAL)
    category = models.CharField("Категория", max_length=150)
    amount = models.DecimalField(
        "Сумма",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    reference_key = models.CharField("Служебный ключ", max_length=255, blank=True, unique=True, null=True)
    comment = models.TextField("Комментарий", blank=True)
    client = models.ForeignKey(
        "crm.Client",
        verbose_name="Клиент",
        related_name="accounting_entries",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    order = models.ForeignKey(
        "crm.Order",
        verbose_name="Заказ",
        related_name="accounting_entries",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ("-date", "-created_at")
        verbose_name = "Операция бухгалтерии"
        verbose_name_plural = "Операции бухгалтерии"

    def __str__(self) -> str:
        return f"{self.get_operation_type_display()} - {self.amount}"
