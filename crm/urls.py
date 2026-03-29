from django.urls import path

from .views import (
    ClientListView,
    ClientMaterialsDownloadView,
    ClientUpdateView,
    OrderCreateView,
    OrderDetailView,
    OrderListView,
    OrderStatusUpdateView,
    OrderUpdateView,
    PaymentCheckView,
)

urlpatterns = [
    path("clients/", ClientListView.as_view(), name="crm_client_list"),
    path("clients/<int:pk>/edit/", ClientUpdateView.as_view(), name="crm_client_edit"),
    path("clients/<int:pk>/materials/download/", ClientMaterialsDownloadView.as_view(), name="crm_client_materials_download"),
    path("orders/", OrderListView.as_view(), name="crm_order_list"),
    path("orders/<int:pk>/status/", OrderStatusUpdateView.as_view(), name="crm_order_status_update"),
    path("payments/", PaymentCheckView.as_view(), name="crm_payment_check"),
    path("orders/create/", OrderCreateView.as_view(), name="crm_order_create"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="crm_order_detail"),
    path("orders/<int:pk>/edit/", OrderUpdateView.as_view(), name="crm_order_edit"),
]
