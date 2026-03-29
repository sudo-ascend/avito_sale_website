from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import CreateView, TemplateView
from openpyxl import Workbook

from accounting.models import AccountingEntry
from crm.models import Client, HostingSubscription, Order
from portfolio.models import Project

from .excel import autosize_columns, style_header, workbook_response
from .forms import ManagerUserCreationForm
from .mixins import StaffRequiredMixin, SuperuserRequiredMixin
from .models import ContactInfo, Service


def _is_staff(user):
    return user.is_authenticated and user.is_staff


def logout_view(request):
    logout(request)
    return redirect("home")


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["services"] = Service.objects.filter(is_active=True)
        context["featured_projects"] = Project.objects.filter(is_published=True, is_featured=True)[:3]
        context["contact_info"] = (
            ContactInfo.objects.filter(is_primary=True).first() or ContactInfo.objects.first()
        )
        return context


class ContactView(TemplateView):
    template_name = "core/contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contact_info"] = (
            ContactInfo.objects.filter(is_primary=True).first() or ContactInfo.objects.first()
        )
        return context


class SiteTypeGuideView(TemplateView):
    template_name = "core/site_type_guide.html"


class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        month_start = today.replace(day=1)
        chart_start = (month_start - timedelta(days=150)).replace(day=1)
        active_orders = Order.objects.filter(
            Q(status__in=[Order.Status.NEW, Order.Status.IN_PROGRESS, Order.Status.DNS_PENDING])
            | Q(hosting_subscription__is_active=True)
        ).distinct()
        accounting = AccountingEntry.objects.all()
        monthly_income = (
            accounting.filter(
                operation_type=AccountingEntry.OperationType.INCOME,
                date__gte=month_start,
            )
            .aggregate(total=Sum("amount"))
            .get("total")
            or Decimal("0")
        )
        monthly_expense = (
            accounting.filter(
                operation_type=AccountingEntry.OperationType.EXPENSE,
                date__gte=month_start,
            )
            .aggregate(total=Sum("amount"))
            .get("total")
            or Decimal("0")
        )
        monthly_subscription_income = (
            accounting.filter(
                operation_type=AccountingEntry.OperationType.INCOME,
                source=AccountingEntry.Source.HOSTING_SUBSCRIPTION,
                date__gte=month_start,
            )
            .aggregate(total=Sum("amount"))
            .get("total")
            or Decimal("0")
        )
        date_limit = today + timedelta(days=14)
        upcoming_expirations = active_orders.filter(
            Q(subscription_end_date__lte=date_limit, subscription_end_date__isnull=False)
            | Q(domain_expiration_date__lte=date_limit, domain_expiration_date__isnull=False)
            | Q(server_expiration_date__lte=date_limit, server_expiration_date__isnull=False)
        ).select_related("client")[:6]
        monthly_totals = (
            accounting.filter(date__gte=chart_start)
            .annotate(month=TruncMonth("date"))
            .values("month", "operation_type", "source")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )
        monthly_total_map = {}
        for item in monthly_totals:
            month_value = item["month"]
            if hasattr(month_value, "date"):
                month_value = month_value.date()
            monthly_total_map[(month_value, item["operation_type"], item["source"])] = item["total"]
        chart_labels = []
        income_chart_data = []
        expense_chart_data = []
        subscription_income_chart_data = []
        profit_chart_data = []
        current_month = chart_start
        while current_month <= month_start:
            income_value = sum(
                value
                for (month_value, operation_type, _source), value in monthly_total_map.items()
                if month_value == current_month and operation_type == AccountingEntry.OperationType.INCOME
            )
            expense_value = sum(
                value
                for (month_value, operation_type, _source), value in monthly_total_map.items()
                if month_value == current_month and operation_type == AccountingEntry.OperationType.EXPENSE
            )
            subscription_income_value = monthly_total_map.get(
                (
                    current_month,
                    AccountingEntry.OperationType.INCOME,
                    AccountingEntry.Source.HOSTING_SUBSCRIPTION,
                ),
                Decimal("0"),
            )
            chart_labels.append(current_month.strftime("%b %Y"))
            income_chart_data.append(float(income_value))
            expense_chart_data.append(float(expense_value))
            subscription_income_chart_data.append(float(subscription_income_value))
            profit_chart_data.append(float(income_value - expense_value))
            next_month_seed = current_month.replace(day=28) + timedelta(days=4)
            current_month = next_month_seed.replace(day=1)

        processed_orders_month = Order.objects.filter(
            status=Order.Status.COMPLETED,
            end_date__gte=month_start,
            end_date__lte=today,
        ).count()
        processed_orders_total = Order.objects.filter(status=Order.Status.COMPLETED).count()

        context.update(
            {
                "monthly_income": monthly_income,
                "monthly_expense": monthly_expense,
                "monthly_subscription_income": monthly_subscription_income,
                "monthly_profit": monthly_income - monthly_expense,
                "recent_orders": Order.objects.select_related("client").order_by("-updated_at")[:5],
                "upcoming_expirations": upcoming_expirations,
                "chart_labels": chart_labels,
                "income_chart_data": income_chart_data,
                "expense_chart_data": expense_chart_data,
                "subscription_income_chart_data": subscription_income_chart_data,
                "profit_chart_data": profit_chart_data,
                "processed_orders_month": processed_orders_month,
                "processed_orders_total": processed_orders_total,
            }
        )
        return context


class ManagerUserCreateView(SuperuserRequiredMixin, CreateView):
    form_class = ManagerUserCreationForm
    template_name = "core/user_form.html"
    success_url = "/dashboard/"

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


@login_required
@user_passes_test(_is_staff)
def export_accounting_xlsx(request):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Бухгалтерия"
    sheet.append(["ID", "Дата", "Тип", "Категория", "Сумма", "Клиент", "Заказ", "Комментарий"])
    for entry in AccountingEntry.objects.select_related("client", "order").order_by(
        "-date", "-created_at"
    ):
        sheet.append(
            [
                entry.pk,
                entry.date.isoformat(),
                entry.get_operation_type_display(),
                entry.category,
                float(entry.amount),
                entry.client.company_name if entry.client else "",
                entry.order.title if entry.order else "",
                entry.comment,
            ]
        )
    style_header(sheet)
    autosize_columns(sheet)
    return workbook_response(workbook, "accounting.xlsx")


@login_required
@user_passes_test(_is_staff)
def export_subscriptions_xlsx(request):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Подписки и оплаты"
    sheet.append(
        [
            "ID заказа",
            "Клиент",
            "Проект",
            "Сумма в месяц",
            "Старт подписки",
            "Следующее поступление",
            "Окончание подписки",
            "Активна",
            "Домен",
        ]
    )
    for subscription in HostingSubscription.objects.select_related("order__client").order_by(
        "next_income_date", "end_date"
    ):
        sheet.append(
            [
                subscription.order.pk,
                subscription.order.client.company_name,
                subscription.order.title,
                float(subscription.monthly_amount),
                subscription.start_date.isoformat() if subscription.start_date else "",
                subscription.next_income_date.isoformat() if subscription.next_income_date else "",
                subscription.end_date.isoformat() if subscription.end_date else "",
                "Да" if subscription.is_active else "Нет",
                subscription.order.domain,
            ]
        )
    style_header(sheet)
    autosize_columns(sheet)
    return workbook_response(workbook, "subscriptions_payments.xlsx")
