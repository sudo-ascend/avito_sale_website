from django.contrib import admin

from .forms import ProjectForm, ProjectImageForm
from .models import Project, ProjectImage


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    form = ProjectImageForm
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectForm
    list_display = ("title", "catalog_order", "completion_date", "is_featured", "is_published")
    list_filter = ("is_featured", "is_published")
    search_fields = ("title", "short_description", "description", "stack_notes")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("catalog_order", "-completion_date")
    inlines = [ProjectImageInline]
