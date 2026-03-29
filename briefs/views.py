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


class BriefCreateView(CreateView):
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
        extras = []
        if self.object.need_hosting:
            extras.append("Хостинг")
        if self.object.need_domain:
            extras.append("Домен")
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
                fail_silently=True,
            )
        except Exception:
            pass
        return response


class BriefSuccessView(TemplateView):
    template_name = "briefs/brief_success.html"
