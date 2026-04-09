from datetime import date

from django import template

register = template.Library()


def _digits_only(value):
    return "".join(char for char in str(value or "") if char.isdigit())


@register.filter
def days_until(value):
    if not value:
        return ""
    return (value - date.today()).days


@register.filter
def expiry_badge_class(value):
    if not value:
        return "bg-secondary-subtle text-secondary-emphasis"
    remaining = (value - date.today()).days
    if remaining < 0:
        return "bg-danger-subtle text-danger-emphasis"
    if remaining <= 7:
        return "bg-warning-subtle text-warning-emphasis"
    if remaining <= 30:
        return "bg-info-subtle text-info-emphasis"
    return "bg-success-subtle text-success-emphasis"


@register.filter
def payment_badge_class(value):
    mapping = {
        "paid": "bg-success-subtle text-success-emphasis",
        "partial": "bg-warning-subtle text-warning-emphasis",
        "unpaid": "bg-secondary-subtle text-secondary-emphasis",
        "overdue": "bg-danger-subtle text-danger-emphasis",
    }
    return mapping.get(value, "bg-secondary-subtle text-secondary-emphasis")


@register.filter
def order_status_badge(value):
    mapping = {
        "new": "bg-secondary-subtle text-secondary-emphasis",
        "in_progress": "bg-primary-subtle text-primary-emphasis",
        "dns_pending": "bg-warning-subtle text-warning-emphasis",
        "completed": "bg-success-subtle text-success-emphasis",
    }
    return mapping.get(value, "bg-secondary-subtle text-secondary-emphasis")


@register.filter
def phone_href(value):
    digits = _digits_only(value)
    if len(digits) == 11 and digits.startswith("8"):
        digits = f"7{digits[1:]}"
    if not digits:
        return ""
    return f"+{digits}" if not digits.startswith("+") else digits


@register.filter
def whatsapp_href(value):
    raw = str(value or "").strip()
    if not raw:
        return ""
    if raw.startswith(("http://", "https://")):
        return raw
    digits = _digits_only(raw)
    if len(digits) == 11 and digits.startswith("8"):
        digits = f"7{digits[1:]}"
    return f"https://wa.me/{digits}" if digits else ""


@register.filter
def telegram_href(value):
    raw = str(value or "").strip()
    if not raw:
        return ""
    if raw.startswith(("http://", "https://")):
        return raw
    return f"https://t.me/{raw.lstrip('@')}"
