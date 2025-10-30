"""
Project URL configuration for Jaston.

Exports:
- admin panel
- explicit auth endpoints (register / login / logout / me / user list)
- drf-spectacular schema + docs
- app-level api v1 includes
- static/media serving in DEBUG
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# Import explicit auth views from apps.users (based on the views you provided)
from apps.users import views as user_views

urlpatterns = [
    # ------------------------
    # Admin panel
    # ------------------------
    path("admin/", admin.site.urls),

    # ------------------------
    # Explicit authentication endpoints (useful for frontend)
    # ------------------------r
    # POST   /api/auth/register/   -> register a new user
    # POST   /api/auth/login/      -> login (token)
    # POST   /api/auth/logout/     -> logout (requires auth)
    # GET    /api/auth/me/         -> current user (requires auth)
    # GET    /api/auth/users/      -> list users (admin only)
    # path("api/auth/register/", user_views.UserRegistrationView.as_view(), name="auth-register"),
    # path("api/auth/login/", user_views.UserLoginView.as_view(), name="auth-login"),
    # path("api/auth/logout/", user_views.UserLogoutView.as_view(), name="auth-logout"),
    # path("api/auth/me/", user_views.CurrentUserView.as_view(), name="auth-current-user"),
    # path("api/auth/users/", user_views.UserListView.as_view(), name="auth-user-list"),

    # Optional: keep DRF browsable auth under a separate prefix if desired
    path("api/auth/drf/", include("rest_framework.urls")),

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
    # API v1 endpoints (app includes / routers)
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
# Custom error handlers
# ------------------------
handler404 = "jaston.handlers.handler404"
handler400 = "jaston.handlers.handler400"
handler403 = "jaston.handlers.handler403"
handler500 = "jaston.handlers.handler500"

# ------------------------
# Serve media & static files during development
# ------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
