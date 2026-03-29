import mimetypes
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404
from django.views.generic import DetailView, ListView

from .models import Project, Technology


class ProjectListView(ListView):
    model = Project
    template_name = "portfolio/project_list.html"
    context_object_name = "projects"

    def get_queryset(self):
        queryset = (
            Project.objects.filter(is_published=True)
            .prefetch_related("technologies")
            .order_by("-completion_date")
        )
        technology_slug = self.request.GET.get("technology")
        if technology_slug:
            queryset = queryset.filter(technologies__slug=technology_slug)
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["technologies"] = Technology.objects.all()
        context["selected_technology"] = self.request.GET.get("technology", "")
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = "portfolio/project_detail.html"
    context_object_name = "project"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Project.objects.filter(is_published=True).prefetch_related("technologies", "images")


def serve_portfolio_site(request, slug, asset_path="index.html"):
    base_dir = (Path(settings.MEDIA_ROOT) / "portfolio" / "sites" / slug).resolve()
    requested_path = (base_dir / asset_path).resolve()
    if not str(requested_path).startswith(str(base_dir)) or not requested_path.exists() or not requested_path.is_file():
        raise Http404("Файл проекта не найден.")

    content_type, encoding = mimetypes.guess_type(str(requested_path))
    response = FileResponse(requested_path.open("rb"), content_type=content_type or "application/octet-stream")
    if encoding:
        response.headers["Content-Encoding"] = encoding
    return response
