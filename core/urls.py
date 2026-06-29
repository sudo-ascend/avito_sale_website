from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("client/", views.HomeView.as_view(), name="client"),
    path("contacts/", views.ContactView.as_view(), name="contact"),
    path("articles/site-types/", views.SiteTypeGuideView.as_view(), name="site_type_guide"),
]
