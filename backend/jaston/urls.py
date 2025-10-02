
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI schema view
schema_view = get_schema_view(
    openapi.Info(
        title="Jaston API",
        default_version="v1",
        description="API documentation for Jaston property management system",
        terms_of_service="https://www.ifinsta.com/terms/",
        contact=openapi.Contact(email="support@ifinsta.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("rest_framework.urls")),
    # Swagger/OpenAPI documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # API v1 endpoints with proper versioning
    path("api/v1/users/", include(("apps.users.urls", "users"), namespace="v1")),
    path("api/v1/properties/", include(("apps.properties.urls", "properties"), namespace="v1")),
    path("api/v1/leases/", include(("apps.leases.urls", "leases"), namespace="v1")),
    path("api/v1/maintenance/", include(("apps.maintenance.urls", "maintenance"), namespace="v1")),
    path("api/v1/messaging/", include(("apps.messaging.urls", "messaging"), namespace="v1")),
    path("api/v1/notifications/", include(("apps.notifications.urls", "notifications"), namespace="v1")),
    path("api/v1/newsletter/", include(("apps.newsletter.urls", "newsletter"), namespace="v1")),
    path("api/v1/cities/", include(("apps.cities.urls", "cities"), namespace="v1")),
    path("api/v1/blog/", include(("apps.blog.urls", "blog"), namespace="v1")),
    path("api/v1/team/", include(("apps.team.urls", "team"), namespace="v1")),
    path("api/v1/appointments/", include(("apps.appointments.urls", "appointments"), namespace="v1")),
    # Core system endpoints
    path("api/v1/", include(("apps.core.urls", "core"), namespace="v1")),
]

# Custom error handlers for JSON responses
handler404 = 'jaston.handlers.handler404'
handler400 = 'jaston.handlers.handler400'
handler403 = 'jaston.handlers.handler403'
handler500 = 'jaston.handlers.handler500'

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
