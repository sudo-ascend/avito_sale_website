from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from core.forms import StaffAuthenticationForm
from core.views import logout_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("portfolio/", include("portfolio.urls")),
    path("briefs/", include("briefs.urls")),
    path("dashboard/crm/", include("crm.urls")),
    path("dashboard/accounting/", include("accounting.urls")),
    path("dashboard/dns/", include("dns_monitor.urls")),
    path("dashboard/notifications/", include("notifications.urls")),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            authentication_form=StaffAuthenticationForm,
        ),
        name="login",
    ),
    path("logout/", logout_view, name="logout"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
