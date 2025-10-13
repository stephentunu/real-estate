from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # ------------------------
    # Admin Panel
    # ------------------------
    path("admin/", admin.site.urls),

    # ------------------------
    # Authentication
    # ------------------------
    path("api/auth/", include("rest_framework.urls")),

    # ------------------------
    # API Schema & Documentation (drf-spectacular)
    # ------------------------
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/docs/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),

    # ------------------------
    # API v1 Endpoints
    # ------------------------
    path("api/v1/users/", include(("apps.users.urls", "users"), namespace="users")),
    path("api/v1/properties/", include(("apps.properties.urls", "properties"), namespace="properties")),
    path("api/v1/leases/", include(("apps.leases.urls", "leases"), namespace="leases")),
    path("api/v1/maintenance/", include(("apps.maintenance.urls", "maintenance"), namespace="maintenance")),
    path("api/v1/messaging/", include(("apps.messaging.urls", "messaging"), namespace="messaging")),
    path("api/v1/notifications/", include(("apps.notifications.urls", "notifications"), namespace="notifications")),
    path("api/v1/newsletter/", include(("apps.newsletter.urls", "newsletter"), namespace="newsletter")),
    path("api/v1/cities/", include(("apps.cities.urls", "cities"), namespace="cities")),
    path("api/v1/blog/", include(("apps.blog.urls", "blog"), namespace="blog")),
    path("api/v1/team/", include(("apps.team.urls", "team"), namespace="team")),
    path("api/v1/appointments/", include(("apps.appointments.urls", "appointments"), namespace="appointments")),

    # Core system endpoints (includes /health and /status)
    path("api/v1/", include(("apps.core.urls", "core"), namespace="core")),
]

# ------------------------
# Custom Error Handlers
# ------------------------
handler404 = "jaston.handlers.handler404"
handler400 = "jaston.handlers.handler400"
handler403 = "jaston.handlers.handler403"
handler500 = "jaston.handlers.handler500"

# ------------------------
# Serve static & media files in development
# ------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
