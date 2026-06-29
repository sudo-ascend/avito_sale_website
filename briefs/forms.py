from decimal import Decimal

from django import forms

from core.forms import BaseStyledModelForm

from .models import BriefAttachment, BriefRequest
from .pricing import (
    EXTRA_PAGE_PRICE as PRICING_EXTRA_PAGE_PRICE,
    HOSTING_PLAN_PRICES as PRICING_HOSTING_PLAN_PRICES,
    OPTIONAL_SERVICE_PRICES as PRICING_OPTIONAL_SERVICE_PRICES,
    SITE_TYPE_PRICES as PRICING_SITE_TYPE_PRICES,
    calculate_estimated_price,
)


class BriefRequestForm(BaseStyledModelForm):
    SITE_TYPE_PRICES = PRICING_SITE_TYPE_PRICES
    EXTRA_PAGE_PRICE = PRICING_EXTRA_PAGE_PRICE
    HOSTING_PLAN_PRICES = PRICING_HOSTING_PLAN_PRICES
    OPTIONAL_SERVICE_PRICES = PRICING_OPTIONAL_SERVICE_PRICES
    OPTIONAL_FIELDS = {
        "extra_pages",
        "photos_files",
        "texts_files",
        "preferred_contact_app",
        "contact_email",
        "client_comment",
        "reference_sites",
        "desired_domain",
        "logo",
        "reviews_files",
        "need_hosting",
        "hosting_plan",
        "need_domain",
        "need_logo_design",
        "need_basic_seo",
        "need_photo_selection",
        "need_email_form",
        "need_reviews_section",
        "need_text_admin_panel",
        "need_catalog_admin_panel",
        "estimated_price",
        "color_template_name",
    }

    photos_files = forms.FileField(label="Фотки", required=True)
    texts_files = forms.FileField(label="Тексты", required=True)
    reviews_files = forms.FileField(label="Скрины отзывов", required=True)

    class Meta:
        model = BriefRequest
        fields = (
            "client_type",
            "business_name",
            "work_region",
            "site_type",
            "extra_pages",
            "color_mode",
            "color_template_name",
            "color_preference",
            "color_accent",
            "color_background",
            "color_extra",
            "reference_sites",
            "desired_domain",
            "logo",
            "need_hosting",
            "hosting_plan",
            "need_domain",
            "need_logo_design",
            "need_basic_seo",
            "need_photo_selection",
            "need_email_form",
            "need_reviews_section",
            "need_text_admin_panel",
            "need_catalog_admin_panel",
            "contact_phone",
            "preferred_contact_app",
            "contact_email",
            "client_comment",
            "estimated_price",
            "privacy_accepted",
        )
        widgets = {
            "color_mode": forms.HiddenInput(),
            "color_template_name": forms.HiddenInput(),
            "color_preference": forms.HiddenInput(),
            "color_accent": forms.HiddenInput(),
            "color_background": forms.HiddenInput(),
            "color_extra": forms.HiddenInput(),
            "extra_pages": forms.NumberInput(attrs={"min": 0, "step": 1}),
            "reference_sites": forms.Textarea(attrs={"rows": 3}),
            "desired_domain": forms.TextInput(),
            "client_comment": forms.Textarea(attrs={"rows": 4}),
            "estimated_price": forms.HiddenInput(),
            "privacy_accepted": forms.CheckboxInput(),
            "need_hosting": forms.CheckboxInput(),
            "need_domain": forms.CheckboxInput(),
            "need_logo_design": forms.CheckboxInput(),
            "need_basic_seo": forms.CheckboxInput(),
            "need_photo_selection": forms.CheckboxInput(),
            "need_email_form": forms.CheckboxInput(),
            "need_reviews_section": forms.CheckboxInput(),
            "need_text_admin_panel": forms.CheckboxInput(),
            "need_catalog_admin_panel": forms.CheckboxInput(),
        }
        labels = {
            "client_type": "Тип клиента",
            "business_name": "Имя / наименование компании",
            "work_region": "Адрес / регион работы",
            "site_type": "Тип сайта",
            "extra_pages": "Дополнительные страницы",
            "color_preference": "Основной",
            "color_accent": "Акцент",
            "color_background": "Фон",
            "color_extra": "Дополнительно",
            "reference_sites": "Ссылки на примеры сайтов",
            "desired_domain": "Желаемый домен",
            "logo": "Логотип",
            "need_hosting": "Хостинг сайта",
            "hosting_plan": "Оплата хостинга",
            "need_domain": "Регистрация домена",
            "need_logo_design": "Создание логотипа",
            "need_basic_seo": "Базовое SEO продвижение",
            "need_photo_selection": "Подбор фото и картинок",
            "need_email_form": "Форма с отправкой писем",
            "need_reviews_section": "Секция с отзывами",
            "need_text_admin_panel": "Админ панель для смены текстов сайта",
            "need_catalog_admin_panel": "Админ панель для редактирования каталога товаров",
            "contact_phone": "Номер телефона",
            "preferred_contact_app": "Предпочитаемое приложение для связи",
            "client_comment": "Комментарий",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.help_text = ""
            field.required = name not in self.OPTIONAL_FIELDS
            if isinstance(field.widget, forms.HiddenInput):
                field.widget.attrs.pop("required", None)
            elif isinstance(field.widget, forms.CheckboxInput):
                if field.required and name == "privacy_accepted":
                    field.widget.attrs["required"] = "required"
                else:
                    field.widget.attrs.pop("required", None)
            elif field.required:
                field.widget.attrs["required"] = "required"
            else:
                field.widget.attrs.pop("required", None)

        self.fields["preferred_contact_app"].choices = [
            ("", "Не выбрано"),
            *BriefRequest.ContactApp.choices,
        ]
        self.fields["hosting_plan"].choices = [
            (BriefRequest.HostingPlan.MONTHLY, "1 месяц — 750 ₽"),
            (BriefRequest.HostingPlan.QUARTERLY, "3 месяца — 1 687,50 ₽"),
        ]
        self.fields["preferred_contact_app"].initial = ""
        self.fields["site_type"].initial = BriefRequest.SiteType.SINGLE_PAGE
        self.fields["estimated_price"].initial = self.SITE_TYPE_PRICES[BriefRequest.SiteType.SINGLE_PAGE]
        self.fields["extra_pages"].initial = 0
        self.fields["need_hosting"].initial = False
        self.fields["hosting_plan"].initial = BriefRequest.HostingPlan.MONTHLY
        self.fields["need_domain"].initial = False
        self.fields["need_logo_design"].initial = False
        self.fields["need_basic_seo"].initial = False
        self.fields["need_photo_selection"].initial = False
        self.fields["need_email_form"].initial = False
        self.fields["need_reviews_section"].initial = False
        self.fields["need_text_admin_panel"].initial = False
        self.fields["need_catalog_admin_panel"].initial = False
        self.fields["color_mode"].initial = BriefRequest.ColorMode.TEMPLATE
        self.fields["color_preference"].initial = "#14344c"
        self.fields["color_accent"].initial = "#c96f3b"
        self.fields["color_background"].initial = "#f4f1ea"
        self.fields["color_extra"].initial = "#2b506b"
        self.fields["privacy_accepted"].error_messages["required"] = "Подтвердите согласие на обработку данных."
        self.fields["desired_domain"].help_text = "Домен — это адрес сайта в браузере, например example.ru."
        self.fields["desired_domain"].widget.attrs.update({"placeholder": "example.ru"})
        self.fields["client_comment"].widget.attrs.update(
            {
                "placeholder": "Если есть уточнения, напишите их здесь.",
            }
        )
        self.fields["extra_pages"].widget.attrs.update(
            {
                "placeholder": "0",
                "inputmode": "numeric",
            }
        )
        self.fields["contact_phone"].widget.attrs.update(
            {
                "placeholder": "+7 (999) 123-45-67",
                "inputmode": "numeric",
                "autocomplete": "tel-national",
                "data-phone-input": "true",
                "data-phone-digits": "10",
            }
        )

    def clean(self):
        cleaned_data = super().clean()
        site_type = cleaned_data.get("site_type")
        extra_pages = cleaned_data.get("extra_pages") or 0
        need_hosting = cleaned_data.get("need_hosting")
        hosting_plan = cleaned_data.get("hosting_plan") or BriefRequest.HostingPlan.MONTHLY
        need_domain = cleaned_data.get("need_domain")
        need_logo_design = cleaned_data.get("need_logo_design")
        need_basic_seo = cleaned_data.get("need_basic_seo")
        need_photo_selection = cleaned_data.get("need_photo_selection")
        need_email_form = cleaned_data.get("need_email_form")
        need_reviews_section = cleaned_data.get("need_reviews_section")
        need_text_admin_panel = cleaned_data.get("need_text_admin_panel")
        need_catalog_admin_panel = cleaned_data.get("need_catalog_admin_panel")

        color_mode = cleaned_data.get("color_mode") or BriefRequest.ColorMode.TEMPLATE
        if color_mode == BriefRequest.ColorMode.TEMPLATE and not cleaned_data.get("color_template_name"):
            raise forms.ValidationError("Выберите шаблон палитры из наших работ.")
        if color_mode == BriefRequest.ColorMode.CUSTOM:
            cleaned_data["color_template_name"] = ""

        if not cleaned_data.get("preferred_contact_app"):
            cleaned_data["preferred_contact_app"] = BriefRequest.ContactApp.WHATSAPP

        if not need_hosting:
            hosting_plan = BriefRequest.HostingPlan.MONTHLY

        cleaned_data["extra_pages"] = extra_pages
        cleaned_data["hosting_plan"] = hosting_plan
        total = calculate_estimated_price(
            site_type=site_type,
            extra_pages=extra_pages,
            need_hosting=need_hosting,
            hosting_plan=hosting_plan,
            need_domain=need_domain,
            need_logo_design=need_logo_design,
            need_basic_seo=need_basic_seo,
            need_photo_selection=need_photo_selection,
            need_email_form=need_email_form,
            need_reviews_section=need_reviews_section,
            need_text_admin_panel=need_text_admin_panel,
            need_catalog_admin_panel=need_catalog_admin_panel,
        )
        cleaned_data["estimated_price"] = total
        return cleaned_data

    def clean_contact_phone(self):
        value = (self.cleaned_data.get("contact_phone") or "").strip()
        digits = "".join(char for char in value if char.isdigit())

        if len(digits) == 11 and digits.startswith(("7", "8")):
            digits = digits[1:]

        if len(digits) != 10:
            raise forms.ValidationError("Введите 10 цифр номера телефона.")

        return f"+7{digits}"

    def _clean_multiple_files(self, field_name):
        uploaded_files = [uploaded_file for uploaded_file in self.files.getlist(field_name) if uploaded_file]
        if self.fields[field_name].required and not uploaded_files:
            raise forms.ValidationError("Добавьте хотя бы один файл.")
        return uploaded_files

    def clean_photos_files(self):
        return self._clean_multiple_files("photos_files")

    def clean_texts_files(self):
        return self._clean_multiple_files("texts_files")

    def clean_reviews_files(self):
        return self._clean_multiple_files("reviews_files")

    def _save_multiple_files(self, brief):
        attachment_groups = (
            (BriefAttachment.Category.PHOTOS, self.cleaned_data.get("photos_files", [])),
            (BriefAttachment.Category.TEXTS, self.cleaned_data.get("texts_files", [])),
            (BriefAttachment.Category.REVIEWS, self.cleaned_data.get("reviews_files", [])),
        )
        for category, uploaded_files in attachment_groups:
            for uploaded_file in uploaded_files:
                BriefAttachment.objects.create(
                    brief=brief,
                    category=category,
                    file=uploaded_file,
                )

    def save(self, commit=True):
        brief = super().save(commit=False)
        brief.estimated_price = self.cleaned_data.get("estimated_price", Decimal("0"))
        if commit:
            brief.save()
            self.save_m2m()
            self._save_multiple_files(brief)
        return brief

    @property
    def pricing_config(self):
        return {
            "site_type_prices": {key: float(value) for key, value in self.SITE_TYPE_PRICES.items()},
            "extra_page_price": float(self.EXTRA_PAGE_PRICE),
            "hosting_plan_prices": {key: float(value) for key, value in self.HOSTING_PLAN_PRICES.items()},
            "addon_prices": {key: float(value) for key, value in self.OPTIONAL_SERVICE_PRICES.items()},
            "hosting_summary_labels": {
                BriefRequest.HostingPlan.MONTHLY: "Хостинг сайта",
                BriefRequest.HostingPlan.QUARTERLY: "Хостинг сайта на 3 месяца",
            },
            "addon_summary_labels": {
                "extra_pages": "Доп. страницы",
                "need_domain": "Регистрация домена",
                "need_logo_design": "Создание логотипа",
                "need_basic_seo": "Базовое SEO",
                "need_photo_selection": "Подбор фото и картинок",
                "need_email_form": "Форма с отправкой писем",
                "need_reviews_section": "Секция с отзывами",
                "need_text_admin_panel": "Админ панель для смены текстов сайта",
                "need_catalog_admin_panel": "Админ панель для редактирования каталога товаров",
            },
        }
