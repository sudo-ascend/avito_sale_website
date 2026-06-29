from django.contrib import admin

from .forms import ProjectForm, ProjectImageForm, TechnologyForm
from .models import Project, ProjectImage, Technology


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    form = ProjectImageForm
    extra = 1


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    form = TechnologyForm
    list_display = ("name", "order", "color", "updated_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    ordering = ("order", "name")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectForm
    list_display = ("title", "catalog_order", "completion_date", "is_featured", "is_published")
    list_filter = ("is_featured", "is_published", "technologies")
    search_fields = ("title", "short_description", "description")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("catalog_order", "-completion_date")
    inlines = [ProjectImageInline]
