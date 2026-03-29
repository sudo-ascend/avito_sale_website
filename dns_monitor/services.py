import dns.resolver
from dns.exception import DNSException
from django.utils import timezone

from crm.models import Order

from .models import DNSCheckLog, DNSMonitorTarget


ACTIVE_ORDER_STATUSES = [
    Order.Status.NEW,
    Order.Status.IN_PROGRESS,
    Order.Status.DNS_PENDING,
]


def normalize_value(value: str) -> str:
    return (value or "").strip().rstrip(".").lower()


def sync_targets_from_orders():
    queryset = (
        Order.objects.filter(status__in=ACTIVE_ORDER_STATUSES)
        .exclude(domain="")
        .exclude(server_ip__isnull=True)
    )
    for order in queryset:
        target, created = DNSMonitorTarget.objects.get_or_create(
            order=order,
            defaults={
                "domain": order.domain,
                "record_type": DNSMonitorTarget.RecordType.A,
                "expected_value": order.server_ip,
            },
        )
        if not created:
            updated_fields = []
            if not target.domain and order.domain:
                target.domain = order.domain
                updated_fields.append("domain")
            if not target.expected_value and order.server_ip and target.record_type == DNSMonitorTarget.RecordType.A:
                target.expected_value = order.server_ip
                updated_fields.append("expected_value")
            if updated_fields:
                target.save(update_fields=updated_fields)


def resolve_dns_values(domain: str, record_type: str) -> list[str]:
    answers = dns.resolver.resolve(domain, record_type)
    values = []
    for answer in answers:
        if record_type == DNSMonitorTarget.RecordType.TXT:
            values.append("".join(part.decode() if isinstance(part, bytes) else part for part in answer.strings))
        elif record_type == DNSMonitorTarget.RecordType.CNAME:
            values.append(str(answer.target).rstrip("."))
        else:
            values.append(getattr(answer, "address", str(answer).rstrip(".")))
    return sorted(set(filter(None, values)))


def run_dns_check_for_target(target: DNSMonitorTarget) -> dict:
    previous_status = target.last_status
    try:
        values = resolve_dns_values(target.domain, target.record_type)
        normalized_values = {normalize_value(value) for value in values}
        status = (
            DNSMonitorTarget.Status.UPDATED
            if normalize_value(target.expected_value) in normalized_values
            else DNSMonitorTarget.Status.NOT_UPDATED
        )
        message = (
            "DNS-запись соответствует ожидаемому значению."
            if status == DNSMonitorTarget.Status.UPDATED
            else "Ожидаемая DNS-запись пока не найдена."
        )
    except DNSException as exc:
        values = []
        status = DNSMonitorTarget.Status.ERROR
        message = f"Ошибка DNS: {exc}"
    except Exception as exc:
        values = []
        status = DNSMonitorTarget.Status.ERROR
        message = f"Непредвиденная ошибка: {exc}"

    now = timezone.now()
    target.last_status = status
    target.last_checked_at = now
    target.last_resolved_value = ", ".join(values)
    target.last_message = message
    target.save(
        update_fields=[
            "last_status",
            "last_checked_at",
            "last_resolved_value",
            "last_message",
        ]
    )

    DNSCheckLog.objects.create(
        target=target,
        status=status,
        resolved_value=", ".join(values),
        message=message,
        response_payload=values,
    )

    notification_sent = False
    if status == DNSMonitorTarget.Status.UPDATED and previous_status != DNSMonitorTarget.Status.UPDATED:
        from notifications.services import send_dns_update_notification

        notification_sent = send_dns_update_notification(target, values)
        if notification_sent:
            target.last_success_notification_at = now
            target.save(update_fields=["last_success_notification_at"])

    return {
        "target_id": target.pk,
        "domain": target.domain,
        "status": status,
        "message": message,
        "values": values,
        "notification_sent": notification_sent,
    }


def run_dns_checks() -> dict:
    sync_targets_from_orders()
    summary = {"checked": 0, "updated": 0, "not_updated": 0, "errors": 0, "results": []}
    queryset = DNSMonitorTarget.objects.filter(is_active=True).select_related("order")
    for target in queryset:
        if target.order and target.order.status == Order.Status.COMPLETED:
            continue
        result = run_dns_check_for_target(target)
        summary["checked"] += 1
        summary["results"].append(result)
        if result["status"] == DNSMonitorTarget.Status.UPDATED:
            summary["updated"] += 1
        elif result["status"] == DNSMonitorTarget.Status.NOT_UPDATED:
            summary["not_updated"] += 1
        else:
            summary["errors"] += 1
    return summary
