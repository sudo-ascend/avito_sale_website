from datetime import timedelta
from io import BytesIO
from pathlib import Path
import zipfile

from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.utils import timezone
from django.views.generic import CreateView, ListView, RedirectView, TemplateView, UpdateView, View

from core.mixins import StaffRequiredMixin

from .forms import ClientForm, OrderEditForm, OrderForm
from .models import Client, Order


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg", ".avif"}


def _build_material_item(*, brief, category, field_file):
    file_name = Path(field_file.name).name
    return {
        "brief": brief,
        "brief_id": brief.pk,
        "category": category,
        "file": field_file,
        "filename": file_name,
        "is_image": Path(file_name).suffix.lower() in IMAGE_EXTENSIONS,
    }


def _collect_brief_materials(brief):
    materials = []
    for attachment in brief.photo_attachments:
        materials.append(_build_material_item(brief=brief, category="photos", field_file=attachment.file))
    for attachment in brief.text_attachments:
        materials.append(_build_material_item(brief=brief, category="texts", field_file=attachment.file))
    for attachment in brief.review_attachments:
        materials.append(_build_material_item(brief=brief, category="reviews", field_file=attachment.file))

    legacy_fields = (
        ("photos", brief.photos_file),
        ("texts", brief.texts_file),
        ("reviews", brief.reviews_file),
        ("logo", brief.logo),
    )
    for category, field_file in legacy_fields:
        if field_file:
            materials.append(_build_material_item(brief=brief, category=category, field_file=field_file))
    return materials


def _collect_client_materials(client):
    orders = (
        client.orders.select_related("brief")
        .prefetch_related("brief__attachments")
        .order_by("-updated_at")
    )
    seen_brief_ids = set()
    materials = []
    briefs = []

    for order in orders:
        if not order.brief_id or order.brief_id in seen_brief_ids:
            continue
        seen_brief_ids.add(order.brief_id)
        briefs.append(order.brief)
        materials.extend(_collect_brief_materials(order.brief))

    return {
        "briefs": briefs,
        "materials": materials,
        "photo_materials": [item for item in materials if item["category"] == "photos" and item["is_image"]],
        "photo_file_materials": [item for item in materials if item["category"] == "photos" and not item["is_image"]],
        "text_materials": [item for item in materials if item["category"] == "texts"],
        "review_materials": [item for item in materials if item["category"] == "reviews"],
        "logo_materials": [item for item in materials if item["category"] == "logo"],
    }


def _build_zip_archive_name(material, used_names):
    base_name = f"brief-{material['brief_id']}/{material['category']}/{material['filename']}"
    archive_name = base_name
    suffix = 1
    while archive_name in used_names:
        stem = Path(base_name).stem
        extension = Path(base_name).suffix
        archive_name = str(Path(base_name).with_name(f"{stem}-{suffix}{extension}"))
        suffix += 1
    used_names.add(archive_name)
    return archive_name


class ClientListView(StaffRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy("crm_order_list")

class ClientUpdateView(StaffRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "crm/client_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_order_id = self.request.GET.get("order")
        client_orders = list(
            self.object.orders.select_related("brief").prefetch_related("brief__attachments").order_by("-updated_at")
        )
        if selected_order_id:
            try:
                selected_order_id = int(selected_order_id)
            except (TypeError, ValueError):
                selected_order_id = None
        else:
            selected_order_id = None

        if selected_order_id:
            client_orders.sort(key=lambda order: (order.pk != selected_order_id, -order.pk))

        selected_order = client_orders[0] if client_orders else None
        material_context = _collect_client_materials(self.object)
        context.update(material_context)
        context["client_orders"] = client_orders
        context["selected_order"] = selected_order
        context["selected_order_id"] = selected_order.pk if selected_order else None
        context["has_orders"] = bool(client_orders)
        context["has_materials"] = bool(material_context["materials"])
        return context

    def get_success_url(self):
        base_url = reverse_lazy("crm_client_edit", kwargs={"pk": self.object.pk})
        selected_order_id = self.request.GET.get("order")
        if selected_order_id:
            return f"{base_url}?order={selected_order_id}#order-panel"
        return base_url


class OrderListView(StaffRequiredMixin, ListView):
    model = Order
    template_name = "crm/order_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        queryset = Order.objects.select_related("client", "brief")
        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q)
                | Q(client__company_name__icontains=q)
                | Q(client__name__icontains=q)
                | Q(domain__icontains=q)
                | Q(comments__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = Order.Status.choices
        return context


class OrderCreateView(StaffRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = "crm/order_form.html"

    def get_success_url(self):
        return self.object.get_absolute_url()


class OrderUpdateView(StaffRequiredMixin, UpdateView):
    model = Order
    form_class = OrderEditForm
    template_name = "crm/order_edit_form.html"

    def get_queryset(self):
        return Order.objects.select_related("client", "brief")

    def get_success_url(self):
        return self.object.get_absolute_url()


class OrderDetailView(StaffRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        order = get_object_or_404(Order.objects.select_related("client"), pk=kwargs["pk"])
        return order.get_absolute_url()


class PaymentCheckView(StaffRequiredMixin, TemplateView):
    template_name = "crm/payment_check.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        soon_limit = today + timedelta(days=14)
        base_queryset = Order.objects.select_related("client").exclude(status=Order.Status.COMPLETED)
        payable_orders = base_queryset.filter(next_payment_date__isnull=False).exclude(
            payment_status=Order.PaymentStatus.PAID
        )

        context.update(
            {
                "overdue_orders": payable_orders.filter(next_payment_date__lt=today).order_by(
                    "next_payment_date"
                ),
                "upcoming_orders": payable_orders.filter(
                    next_payment_date__gte=today,
                    next_payment_date__lte=soon_limit,
                ).order_by("next_payment_date"),
                "unscheduled_orders": base_queryset.filter(
                    Q(payment_status=Order.PaymentStatus.UNPAID)
                    | Q(payment_status=Order.PaymentStatus.PARTIAL)
                    | Q(payment_status=Order.PaymentStatus.OVERDUE),
                    next_payment_date__isnull=True,
                ).order_by("-updated_at"),
            }
        )
        return context


class ClientMaterialsDownloadView(StaffRequiredMixin, View):
    def get(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        material_context = _collect_client_materials(client)
        materials = material_context["materials"]
        if not materials:
            raise Http404("У клиента нет материалов для скачивания.")

        buffer = BytesIO()
        used_names = set()
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for material in materials:
                field_file = material["file"]
                try:
                    field_file.open("rb")
                    archive.writestr(
                        _build_zip_archive_name(material, used_names),
                        field_file.read(),
                    )
                finally:
                    try:
                        field_file.close()
                    except Exception:
                        pass

        safe_name = slugify(client.company_name) or f"client-{client.pk}"
        response = HttpResponse(buffer.getvalue(), content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="{safe_name}-materials.zip"'
        return response


class OrderStatusUpdateView(StaffRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        new_status = request.POST.get("status", "")
        allowed_statuses = {value for value, _ in Order.Status.choices}
        if new_status in allowed_statuses and order.status != new_status:
            order.status = new_status
            order.save(update_fields=["status", "updated_at"])

        next_url = request.POST.get("next") or reverse_lazy("crm_order_list")
        return redirect(next_url)
