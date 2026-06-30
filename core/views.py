from django.views.generic import TemplateView

from briefs.pricing import (
    EXTRA_PAGE_PRICE,
    HOME_COMMON_BUNDLE_KEYS,
    HOME_SERVICE_BUNDLES,
    HOSTING_PLAN_PRICES,
    OPTIONAL_SERVICE_PRICES,
    SITE_TYPE_PRICES,
)
from portfolio.models import Project

from .contact_data import get_primary_contact


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projects = list(
            Project.objects.filter(is_published=True)
            .prefetch_related("images")
            .order_by("catalog_order", "-completion_date", "-created_at")
        )
        site_content = get_primary_contact()

        context["featured_projects"] = projects[:9]
        context["hero_project"] = projects[0] if projects else None
        context["popular_projects"] = projects[:6]
        context["suggested_projects"] = projects[3:6] or projects[:3]
        context["catalog_projects"] = projects[:6]
        context["contact_info"] = site_content
        context["site_content"] = site_content
        context["bundle_services"] = [
            service for service in HOME_SERVICE_BUNDLES if service["key"] in HOME_COMMON_BUNDLE_KEYS
        ]
        context["extra_bundle_services"] = [
            service for service in HOME_SERVICE_BUNDLES if service["key"] not in HOME_COMMON_BUNDLE_KEYS
        ]
        context["home_service_config"] = {
            "site_type_prices": {key: float(value) for key, value in SITE_TYPE_PRICES.items()},
            "extra_page_price": float(EXTRA_PAGE_PRICE),
            "hosting_plan_prices": {key: float(value) for key, value in HOSTING_PLAN_PRICES.items()},
            "addon_prices": {key: float(value) for key, value in OPTIONAL_SERVICE_PRICES.items()},
        }
        context["project_metrics"] = {
            "project_count": Project.objects.filter(is_published=True).count(),
            "technology_count": len(
                {
                    item.strip()
                    for project in projects
                    for item in (project.stack_notes or "").split(",")
                    if item.strip()
                }
            ),
        }
        return context


class ContactView(TemplateView):
    template_name = "core/contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site_content = get_primary_contact()
        context["contact_info"] = site_content
        context["site_content"] = site_content
        return context


class SiteTypeGuideView(TemplateView):
    template_name = "core/site_type_guide.html"
