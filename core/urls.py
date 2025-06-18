"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

"""
URL configuration for core project.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger Schema Configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Verboheit Math League API",
        default_version='v1',
        description="API documentation for the VML Competition Web Platform",
        terms_of_service="https://yourdomain.com/terms/",
        contact=openapi.Contact(
            name="VML Support",
            email="support@verboheit.com",
            url="https://support.verboheit.com"
        ),
        license=openapi.License(
            name="Proprietary License",
            url="https://yourdomain.com/license/"
        ),
        x_logo={
            "url": "https://yourdomain.com/static/logo.png",
            "backgroundColor": "#FFFFFF",
            "altText": "VML Logo"
        }
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    url=settings.BASE_URL if hasattr(settings, 'BASE_URL') else None,
    authentication_classes=[],
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include([
        path('v1/', include('api.urls', namespace='v1')),
        path('', RedirectView.as_view(url='/api/v1/', permanent=False)),
    ])),
    
    # Swagger and ReDoc - versioned documentation
    re_path(r'^swagger/v1(?P<format>\.json|\.yaml)$', 
            schema_view.without_ui(cache_timeout=0), 
            name='schema-json-v1'),
    path('swagger/v1/', 
         schema_view.with_ui('swagger', cache_timeout=0), 
         name='schema-swagger-ui-v1'),
    path('redoc/v1/', 
         schema_view.with_ui('redoc', cache_timeout=0), 
         name='schema-redoc-v1'),
    
    # Redirects to current version docs
    path('swagger/', RedirectView.as_view(url='/swagger/v1/', permanent=False)),
    path('redoc/', RedirectView.as_view(url='/redoc/v1/', permanent=False)),
]

# Debug toolbar for development
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns