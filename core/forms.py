from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class BootstrapFormMixin:
    input_class = "form-control"
    select_class = "form-select"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            existing_class = widget.attrs.get("class", "")
            if isinstance(widget, forms.ColorInput):
                css_class = "form-control form-control-color"
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                css_class = self.select_class
            elif isinstance(widget, forms.CheckboxInput):
                css_class = "form-check-input"
            elif isinstance(widget, (forms.CheckboxSelectMultiple, forms.RadioSelect)):
                css_class = ""
            else:
                css_class = self.input_class

            widget.attrs["class"] = f"{existing_class} {css_class}".strip()
            if field.required and not isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("required", "required")
            if name in {
                "deadline",
                "start_date",
                "end_date",
                "subscription_end_date",
                "next_payment_date",
                "domain_expiration_date",
                "server_expiration_date",
                "date",
            }:
                widget.attrs.setdefault("type", "date")


class BaseStyledForm(BootstrapFormMixin, forms.Form):
    pass


class BaseStyledModelForm(BootstrapFormMixin, forms.ModelForm):
    pass


class ManagerUserCreationForm(BootstrapFormMixin, UserCreationForm):
    ROLE_MANAGER = "manager"
    ROLE_ADMIN = "admin"
    ROLE_CHOICES = (
        (ROLE_MANAGER, "Менеджер"),
        (ROLE_ADMIN, "Администратор"),
    )

    role = forms.ChoiceField(label="Роль", choices=ROLE_CHOICES)
    email = forms.EmailField(label="Email", required=True)
    first_name = forms.CharField(label="Имя", max_length=150, required=False)
    last_name = forms.CharField(label="Фамилия", max_length=150, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "role")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        user.is_staff = True
        user.is_superuser = self.cleaned_data["role"] == self.ROLE_ADMIN
        if commit:
            user.save()
        return user


class StaffAuthenticationForm(BootstrapFormMixin, AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise forms.ValidationError(
                "Вход доступен только администраторам и менеджерам.",
                code="not_staff",
            )
