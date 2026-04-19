import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from portfolio.models import Project

from .forms import BriefRequestForm
from .models import BriefRequest
from .services import sync_brief_to_crm

logger = logging.getLogger(__name__)


class BriefCreateView(CreateView):
    BOOLEAN_QUERY_FIELDS = (
        "need_hosting",
        "need_domain",
        "need_logo_design",
        "need_basic_seo",
        "need_photo_selection",
        "need_email_form",
        "need_reviews_section",
    )
    SERVICE_QUERY_FIELDS = ("site_type", "extra_pages", "hosting_plan", *BOOLEAN_QUERY_FIELDS)
    TRUTHY_QUERY_VALUES = {"1", "true", "True", "on", "yes"}
    DEFAULT_PROJECT_EXAMPLES = [
        {
            "title": "AutoParts Catalog",
            "short_description": "Каталог с заявками, фильтрами и понятной карточкой товара.",
            "palette_colors": ["#14344c", "#c96f3b", "#f4f1ea", "#2b506b"],
            "image_url": "",
            "url": "",
        },
        {
            "title": "Clinic Booking",
            "short_description": "Сайт услуг с онлайн-записью, расписанием и современным интерфейсом.",
            "palette_colors": ["#0f4c5c", "#1b9aaa", "#edf6f9", "#ff7d00"],
            "image_url": "",
            "url": "",
        },
        {
            "title": "Legal Office",
            "short_description": "Корпоративный сайт юридической компании с акцентом на доверие и структуру.",
            "palette_colors": ["#1f2933", "#b08968", "#f8f5f2", "#4b5563"],
            "image_url": "",
            "url": "",
        },
    ]

    model = BriefRequest
    form_class = BriefRequestForm
    template_name = "briefs/brief_form.html"
    success_url = reverse_lazy("brief_success")

    def should_reset_service_defaults(self):
        return not any(self.request.GET.get(field_name) for field_name in self.SERVICE_QUERY_FIELDS)

    def get_initial(self):
        initial = super().get_initial()
        query = self.request.GET

        if self.should_reset_service_defaults():
            initial.setdefault("site_type", BriefRequest.SiteType.SINGLE_PAGE)
            initial.setdefault("extra_pages", 0)
            initial.setdefault("hosting_plan", BriefRequest.HostingPlan.MONTHLY)
            for field_name in self.BOOLEAN_QUERY_FIELDS:
                initial.setdefault(field_name, False)

        site_type = query.get("site_type")
        if site_type in {choice[0] for choice in BriefRequest.SiteType.choices}:
            initial["site_type"] = site_type

        hosting_plan = query.get("hosting_plan")
        if hosting_plan in {choice[0] for choice in BriefRequest.HostingPlan.choices}:
            initial["hosting_plan"] = hosting_plan

        try:
            extra_pages = max(0, int(query.get("extra_pages", 0)))
        except (TypeError, ValueError):
            extra_pages = 0
        if extra_pages:
            initial["extra_pages"] = extra_pages

        for field_name in self.BOOLEAN_QUERY_FIELDS:
            if query.get(field_name) in self.TRUTHY_QUERY_VALUES:
                initial[field_name] = True

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projects = list(
            Project.objects.filter(is_published=True, is_featured=True)
            .prefetch_related("technologies")
            .order_by("-completion_date")[:3]
        )
        if projects:
            context["brief_project_examples"] = [
                {
                    "title": project.title,
                    "short_description": project.short_description,
                    "palette_colors": project.palette_colors,
                    "image_url": project.cover_image.url if project.cover_image else "",
                    "url": project.get_absolute_url(),
                }
                for project in projects
            ]
        else:
            context["brief_project_examples"] = self.DEFAULT_PROJECT_EXAMPLES

        form = context.get("form")
        context["reset_service_defaults"] = bool(
            form and not form.is_bound and self.should_reset_service_defaults()
        )
        examples = context["brief_project_examples"]
        if form and not form.is_bound and examples:
            first_example = examples[0]
            palette_colors = list(first_example.get("palette_colors", []))
            while len(palette_colors) < 4:
                palette_colors.append("#14344c")
            form.initial.setdefault("color_mode", BriefRequest.ColorMode.TEMPLATE)
            form.initial.setdefault("color_template_name", first_example["title"])
            form.initial.setdefault("color_preference", palette_colors[0])
            form.initial.setdefault("color_accent", palette_colors[1])
            form.initial.setdefault("color_background", palette_colors[2])
            form.initial.setdefault("color_extra", palette_colors[3])
        return context

    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)
            order = sync_brief_to_crm(self.object)
        messages.success(self.request, "ТЗ успешно отправлено. Мы свяжемся с вами в ближайшее время.")
        extras = self.object.selected_extra_services
        color_source = (
            f"Шаблон: {self.object.color_template_name}"
            if self.object.color_mode == self.object.ColorMode.TEMPLATE and self.object.color_template_name
            else "Кастомная палитра"
        )
        try:
            send_mail(
                subject=f"Новая заявка с сайта: {self.object.business_name}",
                message=(
                    f"Название: {self.object.business_name}\n"
                    f"Тип клиента: {self.object.get_client_type_display()}\n"
                    f"Тип сайта: {self.object.get_site_type_display()}\n"
                    f"Доп. страниц: {self.object.extra_pages}\n"
                    f"Email: {self.object.contact_email}\n"
                    f"Телефон: {self.object.contact_phone}\n"
                    f"Предпочитаемая связь: {self.object.get_preferred_contact_app_display()}\n"
                    f"Регион: {self.object.work_region}\n"
                    f"Режим палитры: {color_source}\n"
                    f"Палитра: {self.object.palette_summary}\n"
                    f"Референсы: {self.object.reference_sites}\n"
                    f"Желаемый домен: {self.object.desired_domain or '-'}\n"
                    f"Комментарий клиента: {self.object.client_comment or '-'}\n"
                    f"Доп. услуги: {', '.join(extras) if extras else '-'}\n"
                    f"Ориентировочная стоимость: {self.object.estimated_price} ₽\n"
                    f"CRM-заказ: #{order.pk} {order.title}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.BRIEF_NOTIFICATION_EMAIL],
                fail_silently=False,
            )
        except Exception:
            logger.exception(
                "Failed to send brief notification email",
                extra={"brief_id": self.object.pk, "order_id": order.pk},
            )
        return response


class BriefSuccessView(TemplateView):
    template_name = "briefs/brief_success.html"
