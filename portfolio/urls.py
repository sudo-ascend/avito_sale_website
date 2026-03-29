from django.urls import path

from .views import ProjectDetailView, ProjectListView, serve_portfolio_site

urlpatterns = [
    path("", ProjectListView.as_view(), name="portfolio_list"),
    path("site/<slug:slug>/", serve_portfolio_site, name="portfolio_site"),
    path("site/<slug:slug>/<path:asset_path>", serve_portfolio_site, name="portfolio_site_asset"),
    path("<slug:slug>/", ProjectDetailView.as_view(), name="portfolio_detail"),
]
