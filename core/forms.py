from django import forms


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
