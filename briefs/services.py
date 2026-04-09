from django.db import transaction
from django.utils import timezone

from crm.models import Client, Order


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
