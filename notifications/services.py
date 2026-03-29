from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from crm.models import Order

from .models import NotificationLog, ReminderRule


ACTIVE_ORDER_STATUSES = [
    Order.Status.NEW,
    Order.Status.IN_PROGRESS,
    Order.Status.DNS_PENDING,
]


def active_thresholds() -> list[int]:
    days = list(
        ReminderRule.objects.filter(is_active=True).values_list("days_before", flat=True)
    )
    return sorted(days or [30, 14, 7, 3, 1], reverse=True)


def _send_notification(
    *,
    reference_key: str,
    event_type: str,
    recipient_email: str,
    subject: str,
    message: str,
    order=None,
    dns_target=None,
    target_date=None,
    days_before=None,
):
    existing = NotificationLog.objects.filter(
        reference_key=reference_key,
        status=NotificationLog.Status.SENT,
    )
    if existing.exists():
        return "skipped"

    status = NotificationLog.Status.SENT
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
    except Exception as exc:
        status = NotificationLog.Status.ERROR
        message = f"{message}\n\nОшибка отправки: {exc}"

    NotificationLog.objects.create(
        reference_key=reference_key,
        event_type=event_type,
        order=order,
        dns_target=dns_target,
        recipient_email=recipient_email,
        target_date=target_date,
        days_before=days_before,
        status=status,
        subject=subject,
        message=message,
    )
    return "sent" if status == NotificationLog.Status.SENT else "error"


def send_dns_update_notification(target, values: list[str]) -> bool:
    subject = f"DNS обновился для {target.domain}"
    message = (
        f"Домен: {target.domain}\n"
        f"Тип записи: {target.record_type}\n"
        f"Ожидаемое значение: {target.expected_value}\n"
        f"Получено: {', '.join(values)}"
    )
    reference_key = f"dns:{target.pk}:{timezone.localdate().isoformat()}"
    result = _send_notification(
        reference_key=reference_key,
        event_type=NotificationLog.EventType.DNS_UPDATED,
        recipient_email=settings.NOTIFICATION_EMAIL,
        subject=subject,
        message=message,
        dns_target=target,
        order=target.order,
    )
    return result == "sent"


def send_expiry_notifications() -> dict:
    today = timezone.localdate()
    thresholds = set(active_thresholds())
    summary = {"sent": 0, "errors": 0, "skipped": 0}

    for order in Order.objects.filter(status__in=ACTIVE_ORDER_STATUSES).select_related("client"):
        candidates = [
            (NotificationLog.EventType.SUBSCRIPTION, order.subscription_end_date, "подписки"),
            (NotificationLog.EventType.DOMAIN, order.domain_expiration_date, "домена"),
            (NotificationLog.EventType.SERVER, order.server_expiration_date, "сервера"),
        ]
        for event_type, target_date, label in candidates:
            if not target_date:
                continue
            days_left = (target_date - today).days
            if days_left not in thresholds:
                continue
            reference_key = f"expiry:{order.pk}:{event_type}:{target_date.isoformat()}:{days_left}"
            subject = f"Напоминание: истечение {label} у проекта {order.title}"
            message = (
                f"Клиент: {order.client.company_name}\n"
                f"Проект: {order.title}\n"
                f"Событие: истекает срок {label}\n"
                f"Дата: {target_date:%d.%m.%Y}\n"
                f"Осталось дней: {days_left}"
            )
            result = _send_notification(
                reference_key=reference_key,
                event_type=event_type,
                recipient_email=settings.NOTIFICATION_EMAIL,
                subject=subject,
                message=message,
                order=order,
                target_date=target_date,
                days_before=days_left,
            )
            if result == "sent":
                summary["sent"] += 1
            elif result == "error":
                summary["errors"] += 1
            else:
                summary["skipped"] += 1
    return summary
