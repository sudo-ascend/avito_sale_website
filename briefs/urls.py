from django.urls import path

from .views import BriefCreateView, BriefPdfDownloadView, BriefSuccessView

urlpatterns = [
    path("create/", BriefCreateView.as_view(), name="brief_create"),
    path("success/", BriefSuccessView.as_view(), name="brief_success"),
    path("success/pdf/", BriefPdfDownloadView.as_view(), name="brief_download_pdf"),
]
