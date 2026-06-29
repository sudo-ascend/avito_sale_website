import logging

from django.conf import settings
from django.core.mail import EmailMessage

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


def build_brief_notification_message(brief) -> str:
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
        f"Заявка в админке: #{brief.pk}"
    )


def send_brief_notification(brief) -> None:
    try:
        recipient = get_brief_notification_recipient()
        if not recipient:
            logger.error(
                "Brief notification recipient is not configured",
                extra={"brief_id": brief.pk},
            )
            return

        subject = f"Новая заявка с сайта: {brief.business_name}"
        email = EmailMessage(
            subject=subject,
            body=build_brief_notification_message(brief),
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
            extra={"brief_id": brief.pk},
        )
