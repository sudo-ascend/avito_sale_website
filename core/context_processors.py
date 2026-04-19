from django.conf import settings

from .contact_data import get_primary_contact


def global_settings(request):
    return {
        "primary_contact": get_primary_contact(),
        "site_brand_name": settings.SITE_BRAND_NAME,
    }
