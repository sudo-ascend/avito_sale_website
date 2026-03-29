import calendar

from django.utils import timezone

from accounting.models import AccountingEntry

from .models import HostingSubscription


def add_months(value, months=1):
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


def sync_order_project_income(order):
    if not order.pk:
        return

    reference_key = f"project-payment:{order.pk}"
    auto_entry = AccountingEntry.objects.filter(reference_key=reference_key)
    if order.payment_status != order.PaymentStatus.PAID or not order.price:
        auto_entry.delete()
        return

    if not auto_entry.exists():
        has_manual_income = (
            AccountingEntry.objects.filter(
                order=order,
                operation_type=AccountingEntry.OperationType.INCOME,
            )
            .exclude(source=AccountingEntry.Source.HOSTING_SUBSCRIPTION)
            .exclude(reference_key=reference_key)
            .exists()
        )
        if has_manual_income:
            return

    AccountingEntry.objects.update_or_create(
        reference_key=reference_key,
        defaults={
            "date": order.end_date or timezone.localdate(),
            "operation_type": AccountingEntry.OperationType.INCOME,
            "source": AccountingEntry.Source.PROJECT_PAYMENT,
            "category": "Оплата проекта",
            "amount": order.price,
            "comment": f"Автоматически создано по заказу «{order.title}».",
            "client": order.client,
            "order": order,
        },
    )


def sync_hosting_subscription(order, *, enabled, monthly_amount, start_date, next_income_date, end_date, comment):
    try:
        existing = order.hosting_subscription
    except HostingSubscription.DoesNotExist:
        existing = None
    if not enabled:
        if existing:
            existing.is_active = False
            existing.end_date = end_date or existing.end_date
            existing.comment = comment
            existing.save(update_fields=["is_active", "end_date", "comment", "updated_at"])
        return None

    subscription, _ = HostingSubscription.objects.update_or_create(
        order=order,
        defaults={
            "monthly_amount": monthly_amount,
            "start_date": start_date,
            "next_income_date": next_income_date,
            "end_date": end_date,
            "is_active": True,
            "comment": comment,
        },
    )
    return subscription
