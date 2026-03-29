from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("contacts/", views.ContactView.as_view(), name="contact"),
    path("articles/site-types/", views.SiteTypeGuideView.as_view(), name="site_type_guide"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("dashboard/users/create/", views.ManagerUserCreateView.as_view(), name="user_create"),
    path("dashboard/export/clients/", views.export_clients_xlsx, name="export_clients"),
    path("dashboard/export/orders/", views.export_orders_xlsx, name="export_orders"),
    path("dashboard/export/accounting/", views.export_accounting_xlsx, name="export_accounting"),
    path("dashboard/export/subscriptions/", views.export_subscriptions_xlsx, name="export_subscriptions"),
]
