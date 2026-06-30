from django import forms

from core.forms import BaseStyledModelForm

from .models import Project, ProjectImage


class ProjectForm(BaseStyledModelForm):
    class Meta:
        model = Project
        fields = (
            "title",
            "slug",
            "short_description",
            "description",
            "completion_date",
            "stack_notes",
            "external_url",
            "cover_image",
            "cover_image_alt",
            "color_palette",
            "catalog_order",
            "is_featured",
            "is_published",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "completion_date": forms.DateInput(attrs={"type": "date"}),
            "color_palette": forms.TextInput(
                attrs={"placeholder": "#14344c, #c96f3b, #f4f1ea, #2b506b"}
            ),
        }


class ProjectImageForm(BaseStyledModelForm):
    class Meta:
        model = ProjectImage
        fields = ("image", "caption", "alt_text", "order")
