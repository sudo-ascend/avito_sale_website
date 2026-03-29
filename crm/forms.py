from datetime import timedelta

from django import forms

from core.forms import BaseStyledModelForm

from .models import Client, Order


class ClientForm(BaseStyledModelForm):
    class Meta:
        model = Client
        fields = (
            "name",
            "company_name",
            "email",
            "phone",
            "preferred_contact_app",
            "telegram",
            "website",
            "notes",
        )
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ""
        self.fields["company_name"].widget.attrs.update({"placeholder": "ООО Ромашка"})
        self.fields["name"].widget.attrs.update({"placeholder": "Иван Иванов"})
        self.fields["email"].widget.attrs.update({"placeholder": "client@example.com"})
        self.fields["phone"].widget.attrs.update(
            {
                "placeholder": "9991234567",
                "inputmode": "numeric",
                "autocomplete": "tel-national",
                "data-phone-input": "true",
                "data-phone-digits": "10",
            }
        )
        self.fields["website"].widget.attrs.update({"placeholder": "https://example.com"})
        self.fields["notes"].widget.attrs.update({"placeholder": "Комментарий по клиенту"})


class OrderForm(BaseStyledModelForm):
    server_password = forms.CharField(
        label="Пароль к серверу",
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text=(
            "Пароль шифруется на уровне приложения. Для продакшена используй "
            "отдельный FIELD_ENCRYPTION_KEY."
        ),
    )

    class Meta:
        model = Order
        fields = (
            "client",
            "brief",
            "title",
            "description",
            "status",
            "start_date",
            "end_date",
            "subscription_term_months",
            "subscription_end_date",
            "domain",
            "domain_expiration_date",
            "server_ip",
            "server_username",
            "server_expiration_date",
            "payment_status",
            "next_payment_date",
            "price",
            "comments",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "comments": forms.Textarea(attrs={"rows": 4}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "subscription_end_date": forms.DateInput(attrs={"type": "date"}),
            "domain_expiration_date": forms.DateInput(attrs={"type": "date"}),
            "server_expiration_date": forms.DateInput(attrs={"type": "date"}),
            "next_payment_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        price = cleaned_data.get("price")
        subscription_end_date = cleaned_data.get("subscription_end_date")
        if start_date and end_date and end_date < start_date:
            self.add_error("end_date", "Дата окончания не может быть раньше даты начала.")
        if start_date and subscription_end_date and subscription_end_date < start_date:
            self.add_error(
                "subscription_end_date",
                "Дата окончания подписки не может быть раньше даты начала.",
            )
        if price is not None and price < 0:
            self.add_error("price", "Стоимость не может быть отрицательной.")
        return cleaned_data

    def save(self, commit=True):
        order = super().save(commit=False)
        server_password = self.cleaned_data.get("server_password")
        if server_password:
            order.set_server_password(server_password)
        if commit:
            order.save()
            self.save_m2m()
        return order


class OrderEditForm(BaseStyledModelForm):
    display_name = forms.CharField(label="Имя или наименование", max_length=150)
    client_type = forms.ChoiceField(label="Тип лица", choices=Client.ClientType.choices)

    class Meta:
        model = Order
        fields = (
            "status",
            "payment_status",
            "start_date",
            "subscription_term_days",
            "end_date",
        )
        labels = {
            "status": "Статус заказа",
            "payment_status": "Статус оплаты",
            "start_date": "Дата начала подписки",
            "subscription_term_days": "Количество дней",
            "end_date": "Дата окончания",
        }
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "readonly": "readonly",
                    "data-order-end-date": "true",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        order = self.instance
        self.fields["subscription_term_days"].required = True
        self.fields["subscription_term_days"].min_value = 1
        self.fields["subscription_term_days"].help_text = "Дата окончания считается автоматически."
        self.fields["end_date"].required = False
        self.fields["end_date"].help_text = "Поле заполняется автоматически."

        display_name = ""
        client_type = Client.ClientType.INDIVIDUAL
        if order and order.pk:
            if order.brief_id and order.brief and order.brief.business_name:
                display_name = order.brief.business_name
            else:
                display_name = order.client.company_name or order.client.name

            if getattr(order.client, "client_type", ""):
                client_type = order.client.client_type
            elif order.brief_id and order.brief:
                client_type = order.brief.client_type

        self.fields["display_name"].initial = display_name
        self.fields["client_type"].initial = client_type
        if order and order.pk and not self.initial.get("subscription_term_days"):
            self.initial["subscription_term_days"] = order.subscription_term_days or order.subscription_term_months

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        subscription_term_days = cleaned_data.get("subscription_term_days")

        if start_date and subscription_term_days:
            cleaned_data["end_date"] = start_date + timedelta(days=subscription_term_days - 1)

        return cleaned_data

    def save(self, commit=True):
        order = super().save(commit=False)
        display_name = (self.cleaned_data.get("display_name") or "").strip()
        client_type = self.cleaned_data.get("client_type") or Client.ClientType.INDIVIDUAL
        previous_display_name = ""

        if self.instance.pk:
            if self.instance.brief_id and self.instance.brief:
                previous_display_name = self.instance.brief.business_name
            if not previous_display_name:
                previous_display_name = self.instance.client.company_name or self.instance.client.name

        order.end_date = self.cleaned_data.get("end_date")
        order.subscription_end_date = order.end_date

        client = order.client
        old_client_values = {client.company_name, client.name}
        client.company_name = display_name
        if not client.name or client.name in old_client_values:
            client.name = display_name
        client.client_type = client_type

        if order.brief_id and order.brief:
            order.brief.business_name = display_name
            order.brief.client_type = client_type
            order.title = f"{order.brief.get_site_type_display()} - {display_name}"[:200]
        elif not order.title or (previous_display_name and previous_display_name in order.title):
            order.title = display_name[:200]

        if commit:
            client.save()
            if order.brief_id and order.brief:
                order.brief.save(update_fields=["business_name", "client_type"])
            order.save()
            self.save_m2m()
        return order
