from django.http import Http404, HttpResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView

from portfolio.models import Project

from .forms import BriefRequestForm
from .models import BriefRequest
from .pdf import build_brief_pdf, get_brief_pdf_filename
from .services import send_brief_notification


class BriefCreateView(CreateView):
    BOOLEAN_QUERY_FIELDS = (
        "need_hosting",
        "need_domain",
        "need_logo_design",
        "need_basic_seo",
        "need_photo_selection",
        "need_email_form",
        "need_reviews_section",
        "need_text_admin_panel",
        "need_catalog_admin_panel",
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
            Project.objects.filter(is_published=True)
            .prefetch_related("technologies")
            .order_by("catalog_order", "-completion_date", "-created_at")
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
        response = super().form_valid(form)
        self.request.session["latest_brief_id"] = self.object.pk
        self.request.session.modified = True
        send_brief_notification(self.object)
        return response


class BriefSuccessView(TemplateView):
    template_name = "briefs/brief_success.html"

    def get_brief(self):
        brief_id = self.request.session.get("latest_brief_id")
        if not brief_id:
            return None
        return BriefRequest.objects.filter(pk=brief_id).prefetch_related("attachments").first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brief = self.get_brief()
        context["brief"] = brief
        context["download_url"] = reverse_lazy("brief_download_pdf")
        return context


class BriefPdfDownloadView(View):
    def get_brief(self, request):
        brief_id = request.session.get("latest_brief_id")
        if not brief_id:
            raise Http404("Заявка не найдена.")
        brief = BriefRequest.objects.filter(pk=brief_id).prefetch_related("attachments").first()
        if brief is None:
            raise Http404("Заявка не найдена.")
        return brief

    def get(self, request, *args, **kwargs):
        brief = self.get_brief(request)
        disposition = "inline" if request.GET.get("disposition") == "inline" else "attachment"
        response = HttpResponse(build_brief_pdf(brief), content_type="application/pdf")
        response["Content-Disposition"] = f'{disposition}; filename="{get_brief_pdf_filename(brief)}"'
        return response
