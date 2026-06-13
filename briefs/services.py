import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.db import transaction
from django.utils import timezone

from crm.models import Client, Order

from .pdf import build_brief_pdf, get_brief_pdf_filename

logger = logging.getLogger(__name__)


def normalize_notification_email(recipient: str, *fallbacks: str) -> str:
    candidate = (recipient or "").strip()
    if not candidate:
        for fallback in fallbacks:
            normalized = normalize_notification_email(fallback)
            if normalized:
                return normalized
        return ""

    if "@" in candidate:
        return candidate

    for fallback in fallbacks:
        fallback = (fallback or "").strip()
        if "@" in fallback:
            return f"{candidate}@{fallback.split('@', 1)[1]}"

    return candidate


def get_brief_notification_recipient() -> str:
    return normalize_notification_email(
        getattr(settings, "BRIEF_NOTIFICATION_EMAIL", ""),
        getattr(settings, "EMAIL_HOST_USER", ""),
        getattr(settings, "DEFAULT_FROM_EMAIL", ""),
        getattr(settings, "NOTIFICATION_EMAIL", ""),
    )


def build_order_title(brief) -> str:
    primary_service = brief.get_site_type_display() or "Заявка с сайта"
    title = f"{primary_service} - {brief.business_name}"
    return title[:200]


def build_order_description(brief) -> str:
    parts = []
    parts.append(f"Тип клиента:\n{brief.get_client_type_display()}")
    parts.append(f"Тип сайта:\n{brief.get_site_type_display()}")
    parts.append(f"Доп. страниц:\n{brief.extra_pages}")
    parts.append(f"Адрес / регион:\n{brief.work_region}")
    if brief.color_mode == brief.ColorMode.TEMPLATE and brief.color_template_name:
        parts.append(f"Цветовая схема:\nШаблон {brief.color_template_name}")
    else:
        parts.append("Цветовая схема:\nКастомная палитра")
    parts.append(f"Палитра:\n{brief.palette_summary}")
    if brief.reference_sites:
        parts.append(f"Референсы:\n{brief.reference_sites}")
    if brief.desired_domain:
        parts.append(f"Желаемый домен:\n{brief.desired_domain}")
    if brief.client_comment:
        parts.append(f"Комментарий клиента:\n{brief.client_comment}")
    extras = brief.selected_extra_services
    if extras:
        parts.append(f"Доп. услуги:\n{', '.join(extras)}")
    return "\n\n".join(parts)


def build_brief_notification_message(brief, order) -> str:
    extras = brief.selected_extra_services
    color_source = (
        f"Шаблон: {brief.color_template_name}"
        if brief.color_mode == brief.ColorMode.TEMPLATE and brief.color_template_name
        else "Кастомная палитра"
    )
    return (
        f"Название: {brief.business_name}\n"
        f"Тип клиента: {brief.get_client_type_display()}\n"
        f"Тип сайта: {brief.get_site_type_display()}\n"
        f"Доп. страниц: {brief.extra_pages}\n"
        f"Email: {brief.contact_email or '-'}\n"
        f"Телефон: {brief.contact_phone}\n"
        f"Предпочитаемая связь: {brief.get_preferred_contact_app_display()}\n"
        f"Регион: {brief.work_region}\n"
        f"Режим палитры: {color_source}\n"
        f"Палитра: {brief.palette_summary}\n"
        f"Референсы: {brief.reference_sites or '-'}\n"
        f"Желаемый домен: {brief.desired_domain or '-'}\n"
        f"Комментарий клиента: {brief.client_comment or '-'}\n"
        f"Доп. услуги: {', '.join(extras) if extras else '-'}\n"
        f"Ориентировочная стоимость: {brief.estimated_price} ₽\n"
        f"CRM-заказ: #{order.pk} {order.title}"
    )


def send_brief_notification(brief, order) -> None:
    try:
        recipient = get_brief_notification_recipient()
        if not recipient:
            logger.error(
                "Brief notification recipient is not configured",
                extra={"brief_id": brief.pk, "order_id": order.pk},
            )
            return

        subject = f"Новая заявка с сайта: {brief.business_name}"
        email = EmailMessage(
            subject=subject,
            body=build_brief_notification_message(brief, order),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )
        email.attach(
            get_brief_pdf_filename(brief),
            build_brief_pdf(brief),
            "application/pdf",
        )
        email.send(fail_silently=False)
    except Exception:
        logger.exception(
            "Failed to send brief notification email",
            extra={"brief_id": brief.pk, "order_id": order.pk},
        )


def get_or_create_client_from_brief(brief):
    client = None
    if brief.contact_email:
        client = Client.objects.filter(email__iexact=brief.contact_email).first()
    if not client and brief.contact_phone:
        client = Client.objects.filter(phone=brief.contact_phone).first()

    defaults = {
        "name": brief.business_name,
        "company_name": brief.business_name,
        "email": brief.contact_email,
        "phone": brief.contact_phone,
        "preferred_contact_app": brief.preferred_contact_app,
        "notes": f"Создано автоматически из заявки #{brief.pk}.",
        "status": Client.Status.NEW,
    }

    if client:
        updated = False
        for field_name, value in defaults.items():
            current_value = getattr(client, field_name)
            if not current_value or field_name == "preferred_contact_app":
                if current_value != value:
                    setattr(client, field_name, value)
                    updated = True
        if updated:
            client.save()
        return client

    return Client.objects.create(**defaults)


@transaction.atomic
def sync_brief_to_crm(brief):
    client = get_or_create_client_from_brief(brief)
    order_defaults = {
        "client": client,
        "title": build_order_title(brief),
        "description": build_order_description(brief),
        "status": Order.Status.NEW,
        "start_date": timezone.localdate(),
        "payment_status": Order.PaymentStatus.UNPAID,
        "price": brief.estimated_price,
        "comments": "Заказ создан автоматически из формы заявки на сайте.",
    }
    order, created = Order.objects.get_or_create(
        brief=brief,
        defaults=order_defaults,
    )
    if not created:
        updated = False
        if order.client_id != client.pk:
            order.client = client
            updated = True
        if not order.title:
            order.title = order_defaults["title"]
            updated = True
        if not order.description:
            order.description = order_defaults["description"]
            updated = True
        if not order.price and brief.estimated_price:
            order.price = brief.estimated_price
            updated = True
        if updated:
            order.save()
    return order
