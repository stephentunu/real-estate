from django.apps import AppConfig
from django.contrib import admin
from django.conf import settings


class JastonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jaston'

    def ready(self):
        # Customize admin site headers and titles
        admin.site.site_header = getattr(settings, 'ADMIN_SITE_HEADER', 'Django Administration')
        admin.site.site_title = getattr(settings, 'ADMIN_SITE_TITLE', 'Django Admin')
        admin.site.index_title = getattr(settings, 'ADMIN_INDEX_TITLE', 'Site Administration')