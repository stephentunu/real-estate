from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Import app URLs directly for schema generation
from apps.users import urls as users_urls
from apps.properties import urls as properties_urls
from apps.leases import urls as leases_urls
from apps.maintenance import urls as maintenance_urls
from apps.messaging import urls as messaging_urls
from apps.notifications import urls as notifications_urls
from apps.newsletter import urls as newsletter_urls
from apps.cities import urls as cities_urls
from apps.blog import urls as blog_urls
from apps.team import urls as team_urls
from apps.appointments import urls as appointments_urls
from apps.core import urls as core_urls

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
    patterns=[
        path("api/v1/users/", include(users_urls)),
        path("api/v1/properties/", include(properties_urls)),
        path("api/v1/leases/", include(leases_urls)),
        path("api/v1/maintenance/", include(maintenance_urls)),
        path("api/v1/messaging/", include(messaging_urls)),
        path("api/v1/notifications/", include(notifications_urls)),
        path("api/v1/newsletter/", include(newsletter_urls)),
        path("api/v1/cities/", include(cities_urls)),
        path("api/v1/blog/", include(blog_urls)),
        path("api/v1/team/", include(team_urls)),
        path("api/v1/appointments/", include(appointments_urls)),
        path("api/v1/", include(core_urls)),
    ],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("rest_framework.urls")),
    
    # Swagger/OpenAPI documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API v1 endpoints with unique namespaces
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
    path("api/v1/", include(("apps.core.urls", "core"), namespace="core")),
]

# Custom error handlers
handler404 = 'jaston.handlers.handler404'
handler400 = 'jaston.handlers.handler400'
handler403 = 'jaston.handlers.handler403'
handler500 = 'jaston.handlers.handler500'

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)