from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError

from .models import ContactInfo


def global_settings(request):
    try:
        primary_contact = (
            ContactInfo.objects.filter(is_primary=True).first() or ContactInfo.objects.first()
        )
    except (OperationalError, ProgrammingError):
        primary_contact = None

    return {
        "primary_contact": primary_contact,
        "site_brand_name": settings.SITE_BRAND_NAME,
    }
