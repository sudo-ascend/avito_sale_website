from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, RedirectView, TemplateView
from openpyxl import Workbook

from briefs.pricing import (
    EXTRA_PAGE_PRICE,
    HOME_COMMON_BUNDLE_KEYS,
    HOME_SERVICE_BUNDLES,
    HOSTING_PLAN_PRICES,
    OPTIONAL_SERVICE_PRICES,
    SITE_TYPE_PRICES,
)
from crm.models import Client, Order
from portfolio.models import Project, Technology

from .contact_data import get_primary_contact
from .excel import autosize_columns, style_header, workbook_response
from .forms import ManagerUserCreationForm
from .mixins import StaffRequiredMixin, SuperuserRequiredMixin
from .models import Service


def _is_staff(user):
    return user.is_authenticated and user.is_staff


def logout_view(request):
    logout(request)
    return redirect("home")


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        featured_projects = list(
            Project.objects.filter(is_published=True)
            .prefetch_related("technologies", "images")
            .order_by("-is_featured", "-completion_date", "-created_at")[:9]
        )
        context["featured_projects"] = featured_projects
        context["hero_project"] = featured_projects[0] if featured_projects else None
        context["popular_projects"] = featured_projects[:6]
        context["suggested_projects"] = featured_projects[4:7] or featured_projects[:3]
        context["catalog_projects"] = featured_projects[:4]
        context["contact_info"] = get_primary_contact()
        context["services"] = Service.objects.filter(is_active=True)
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
            "technology_count": Technology.objects.annotate(project_total=Count("projects"))
            .filter(project_total__gt=0)
            .count(),
        }
        return context


class ContactView(TemplateView):
    template_name = "core/contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contact_info"] = get_primary_contact()
        return context


class SiteTypeGuideView(TemplateView):
    template_name = "core/site_type_guide.html"


class DashboardView(StaffRequiredMixin, RedirectView):
    permanent = False
    pattern_name = "crm_order_list"


class ManagerUserCreateView(SuperuserRequiredMixin, CreateView):
    form_class = ManagerUserCreationForm
    template_name = "core/user_form.html"
    success_url = reverse_lazy("crm_order_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Пользователь успешно создан.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Не удалось создать пользователя. Проверь поля формы.")
        return super().form_invalid(form)


@login_required
@user_passes_test(_is_staff)
def export_clients_xlsx(request):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Клиенты"
    sheet.append(["ID", "Имя", "Компания", "Email", "Телефон", "Telegram", "Сайт"])
    for client in Client.objects.order_by("company_name", "name"):
        sheet.append(
            [
                client.pk,
                client.name,
                client.company_name,
                client.email,
                client.phone,
                client.telegram,
                client.website,
            ]
        )
    style_header(sheet)
    autosize_columns(sheet)
    return workbook_response(workbook, "clients.xlsx")


@login_required
@user_passes_test(_is_staff)
def export_orders_xlsx(request):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Заказы"
    sheet.append(
        [
            "ID",
            "Клиент",
            "Проект",
            "Статус",
            "Дата начала",
            "Дата окончания",
            "Домен",
            "IP сервера",
            "Пользователь сервера",
            "Статус оплаты",
            "Следующая оплата",
            "Стоимость",
            "Комментарий",
        ]
    )
    for order in Order.objects.select_related("client").order_by("-updated_at"):
        sheet.append(
            [
                order.pk,
                order.client.company_name,
                order.title,
                order.get_status_display(),
                order.start_date.isoformat() if order.start_date else "",
                order.end_date.isoformat() if order.end_date else "",
                order.domain,
                order.server_ip,
                order.server_username,
                order.get_payment_status_display(),
                order.next_payment_date.isoformat() if order.next_payment_date else "",
                float(order.price),
                order.comments,
            ]
        )
    style_header(sheet)
    autosize_columns(sheet)
    return workbook_response(workbook, "orders.xlsx")
