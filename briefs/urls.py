from django.urls import path

from .views import BriefCreateView, BriefSuccessView

urlpatterns = [
    path("create/", BriefCreateView.as_view(), name="brief_create"),
    path("success/", BriefSuccessView.as_view(), name="brief_success"),
]
