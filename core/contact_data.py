from dataclasses import dataclass

from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError

from .models import ContactInfo


@dataclass(frozen=True)
class ContactSnapshot:
    company_name: str
    email: str
    phone: str
    tagline: str = ""
    telegram: str = ""
    whatsapp: str = ""
    address: str = ""
    working_hours: str = ""
    map_embed_url: str = ""
    is_primary: bool = True


def get_fallback_contact() -> ContactSnapshot:
    return ContactSnapshot(
        company_name=settings.SITE_BRAND_NAME,
        tagline="Сайты, CRM и сопровождение цифровых продуктов",
        email="grachevilia09@yandex.ru",
        phone="79167950225",
    )


def get_primary_contact():
    try:
        contact = ContactInfo.objects.filter(is_primary=True).first() or ContactInfo.objects.first()
    except (OperationalError, ProgrammingError):
        contact = None
    return contact or get_fallback_contact()
