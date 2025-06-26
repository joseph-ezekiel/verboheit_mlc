"""
URL configuration for the Verboheit Math League project.

Includes:
- Admin interface
- API routes with versioning
- Interactive API docs via Swagger and ReDoc (powered by drf-yasg)
- Debug toolbar URLs
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from debug_toolbar.toolbar import debug_toolbar_urls

# === Swagger Schema Configuration ===
schema_view = get_schema_view(
    openapi.Info(
        title="Verboheit Math League API",
        default_version="v1",
        description="API documentation for the VML Competition Web Platform",
        terms_of_service="https://yourdomain.com/terms/",
        contact=openapi.Contact(
            name="VML Support",
            email="support@verboheit.com",
            url="https://support.verboheit.com",
        ),
        license=openapi.License(
            name="Proprietary License",
            url="https://yourdomain.com/license/",
        ),
        x_logo={
            "url": "https://yourdomain.com/static/logo.png",
            "backgroundColor": "#FFFFFF",
            "altText": "VML Logo",
        },
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=[],
    url=getattr(settings, "BASE_URL", None),
)

urlpatterns = [
    # === Admin Panel ===
    path("api/v1/admin/", admin.site.urls),
    # === API ===
    path(
        "api/",
        include(
            [
                path("v1/", include("api.urls", namespace="v1")),
                path("", RedirectView.as_view(url="/api/v1/", permanent=False)),
            ]
        ),
    ),
    # === Swagger / ReDoc (API Docs) ===
    re_path(
        r"^swagger/v1(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json-v1",
    ),
    path(
        "swagger/v1/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui-v1",
    ),
    path(
        "redoc/v1/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc-v1",
    ),
    # === Default redirect to current doc versions ===
    path("swagger/", RedirectView.as_view(url="/swagger/v1/", permanent=False)),
    path("redoc/", RedirectView.as_view(url="/redoc/v1/", permanent=False)),
]

# === Debug Toolbar (Optional, Dev-Only) ===
urlpatterns += debug_toolbar_urls()
