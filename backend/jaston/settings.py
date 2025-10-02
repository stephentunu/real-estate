"""Django settings for Jaston Real Estate platform.

This module provides centralized Django configuration using a modular
environment loader with proper type safety and validation.
"""

from __future__ import annotations

import os
from pathlib import Path
from config.environment import get_env_loader

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment loader
env_loader = get_env_loader()

# Validate configuration on startup
env_loader.validate_all()

# Get configuration objects
security_config = env_loader.get_security_config()
server_config = env_loader.get_server_config()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = security_config.secret_key

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = security_config.debug

ALLOWED_HOSTS = server_config.allowed_hosts

# Application definition
INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "drf_yasg",
    "channels",
    "django_filters",
    "django_extensions",  # Added for debugging URLs
    "apps.core",
    "apps.users",
    "apps.properties",
    "apps.leases",
    "apps.maintenance",
    "apps.media",
    "apps.messaging",
    "apps.notifications",
    "apps.newsletter",
    "apps.cities",
    "apps.blog",
    "apps.team",
    "apps.appointments",
    "jaston.apps.JastonConfig",
]

# Only include development-only apps when DEBUG is True
if not DEBUG:
    # remove dev-only apps from production
    try:
        INSTALLED_APPS.remove('django_extensions')
    except ValueError:
        pass

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "apps.core.middleware.APIErrorMiddleware",  # Add API error handling middleware
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "jaston.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "jaston.wsgi.application"
ASGI_APPLICATION = "jaston.asgi.application"

# Database configuration
from config.database import get_database_config
from config.static_files_config import get_static_files_config, get_media_files_config
from config.email_config import get_email_config
from config.performance_config import get_performance_config
from config.admin_config import get_admin_config
from config.logging_config import get_logging_config
DATABASES = get_database_config()

# Cache configuration  
from config.cache_config import get_cache_config, get_session_config
CACHES = get_cache_config()

# Session configuration
session_cfg = get_session_config()
SESSION_ENGINE = session_cfg.get('SESSION_ENGINE')
SESSION_CACHE_ALIAS = session_cfg.get('SESSION_CACHE_ALIAS')
SESSION_COOKIE_AGE = session_cfg.get('SESSION_COOKIE_AGE')
SESSION_COOKIE_SECURE = session_cfg.get('SESSION_COOKIE_SECURE')
SESSION_COOKIE_HTTPONLY = session_cfg.get('SESSION_COOKIE_HTTPONLY')
SESSION_COOKIE_SAMESITE = session_cfg.get('SESSION_COOKIE_SAMESITE')
SESSION_SAVE_EVERY_REQUEST = session_cfg.get('SESSION_SAVE_EVERY_REQUEST')

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization configuration
from config.deployment import get_internationalization_config
i18n_cfg = get_internationalization_config()
LANGUAGE_CODE = i18n_cfg.get('LANGUAGE_CODE')
TIME_ZONE = i18n_cfg.get('TIME_ZONE')
USE_I18N = i18n_cfg.get('USE_I18N')
USE_TZ = i18n_cfg.get('USE_TZ')
LANGUAGES = i18n_cfg.get('LANGUAGES')
LOCALE_PATHS = i18n_cfg.get('LOCALE_PATHS')

# Security configuration
from config.security_config import (
    get_cors_config,
    get_csrf_config, 
    get_security_headers_config,
    get_auth_config
)
cors_cfg = get_cors_config()
CORS_ALLOW_ALL_ORIGINS = cors_cfg.get('CORS_ALLOW_ALL_ORIGINS')
CORS_ALLOW_CREDENTIALS = cors_cfg.get('CORS_ALLOW_CREDENTIALS')
CORS_ALLOWED_ORIGINS = cors_cfg.get('CORS_ALLOWED_ORIGINS')
CORS_ALLOWED_ORIGIN_REGEXES = cors_cfg.get('CORS_ALLOWED_ORIGIN_REGEXES')

csrf_cfg = get_csrf_config()
CSRF_COOKIE_SECURE = csrf_cfg.get('CSRF_COOKIE_SECURE')
CSRF_COOKIE_HTTPONLY = csrf_cfg.get('CSRF_COOKIE_HTTPONLY')
CSRF_COOKIE_SAMESITE = csrf_cfg.get('CSRF_COOKIE_SAMESITE')
CSRF_USE_SESSIONS = csrf_cfg.get('CSRF_USE_SESSIONS')
CSRF_COOKIE_AGE = csrf_cfg.get('CSRF_COOKIE_AGE')
CSRF_TRUSTED_ORIGINS = csrf_cfg.get('CSRF_TRUSTED_ORIGINS')

sec_headers_cfg = get_security_headers_config()
SECURE_BROWSER_XSS_FILTER = sec_headers_cfg.get('SECURE_BROWSER_XSS_FILTER')
SECURE_CONTENT_TYPE_NOSNIFF = sec_headers_cfg.get('SECURE_CONTENT_TYPE_NOSNIFF')
SECURE_HSTS_INCLUDE_SUBDOMAINS = sec_headers_cfg.get('SECURE_HSTS_INCLUDE_SUBDOMAINS')
SECURE_HSTS_PRELOAD = sec_headers_cfg.get('SECURE_HSTS_PRELOAD')
SECURE_HSTS_SECONDS = sec_headers_cfg.get('SECURE_HSTS_SECONDS')
SECURE_REFERRER_POLICY = sec_headers_cfg.get('SECURE_REFERRER_POLICY')
SECURE_SSL_REDIRECT = sec_headers_cfg.get('SECURE_SSL_REDIRECT')
X_FRAME_OPTIONS = sec_headers_cfg.get('X_FRAME_OPTIONS')

auth_cfg = get_auth_config()
AUTH_USER_MODEL = auth_cfg.get('AUTH_USER_MODEL')
AUTHENTICATION_BACKENDS = auth_cfg.get('AUTHENTICATION_BACKENDS')
LOGIN_URL = auth_cfg.get('LOGIN_URL')
LOGIN_REDIRECT_URL = auth_cfg.get('LOGIN_REDIRECT_URL')
LOGOUT_REDIRECT_URL = auth_cfg.get('LOGOUT_REDIRECT_URL')
PASSWORD_RESET_TIMEOUT = auth_cfg.get('PASSWORD_RESET_TIMEOUT')

# Django REST Framework configuration
from config.drf_config import get_drf_config, get_swagger_config
REST_FRAMEWORK = get_drf_config()

# Swagger/OpenAPI configuration
swagger_cfg = get_swagger_config()
SWAGGER_SETTINGS = swagger_cfg.get('SWAGGER_SETTINGS')
REDOC_SETTINGS = swagger_cfg.get('REDOC_SETTINGS')

# Channels configuration
from config.channels_config import get_channels_config
channels_cfg = get_channels_config()
CHANNEL_LAYERS = channels_cfg.get('CHANNEL_LAYERS')
# ASGI_APPLICATION may already be set above; prefer channels_cfg value if provided
ASGI_APPLICATION = channels_cfg.get('ASGI_APPLICATION', ASGI_APPLICATION)

# Celery configuration
from config.celery_config import get_celery_config
CELERY_CONFIG = get_celery_config()

# Backwards-compatible aliases for older settings access patterns
CELERY_BROKER_URL = CELERY_CONFIG.get('broker_url')
CELERY_RESULT_BACKEND = CELERY_CONFIG.get('result_backend')
CELERY_ACCEPT_CONTENT = CELERY_CONFIG.get('accept_content')
CELERY_TASK_SERIALIZER = CELERY_CONFIG.get('task_serializer')
CELERY_RESULT_SERIALIZER = CELERY_CONFIG.get('result_serializer')
CELERY_TIMEZONE = CELERY_CONFIG.get('timezone')
CELERY_ENABLE_UTC = CELERY_CONFIG.get('enable_utc')
CELERY_TASK_TRACK_STARTED = CELERY_CONFIG.get('task_track_started')
CELERY_TASK_TIME_LIMIT = CELERY_CONFIG.get('task_time_limit')
CELERY_TASK_SOFT_TIME_LIMIT = CELERY_CONFIG.get('task_soft_time_limit')
CELERY_WORKER_PREFETCH_MULTIPLIER = CELERY_CONFIG.get('worker_prefetch_multiplier')
CELERY_WORKER_MAX_TASKS_PER_CHILD = CELERY_CONFIG.get('worker_max_tasks_per_child')
# NOTE: Periodic tasks should be managed via django-celery-beat (database-backed schedules)
# The `CELERY_CONFIG['beat_schedule']` is kept for backward-compatibility, but to avoid
# duplicate/conflicting schedule definitions we do not load it into `CELERY_BEAT_SCHEDULE`.
# Use the django-celery-beat admin or the data migration `apps.core.migrations.0001_seed_celery_beat`
# to manage production schedules.
CELERY_BEAT_SCHEDULE = {}

# Celery Beat settings
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Task routing
CELERY_TASK_ROUTES = {
    'apps.core.tasks.cleanup_soft_deleted_records': {'queue': 'cleanup'},
    'apps.core.tasks.generate_cleanup_report': {'queue': 'reports'},
    'apps.core.tasks.scheduled_cleanup': {'queue': 'maintenance'},
}

# Worker settings
CELERY_TASK_ACKS_LATE = True

# Soft Delete Retention Policies
# Configure how long soft-deleted records are kept before permanent deletion
SOFT_DELETE_RETENTION_POLICIES = {
    # Global default (90 days)
    'default': 90,
    
    # App-level defaults
    'properties': 365,  # Properties kept for 1 year
    'users': 1095,      # User data kept for 3 years (compliance)
    'leases': 2555,     # Lease data kept for 7 years (legal requirement)
    'maintenance': 1095, # Maintenance records kept for 3 years
    'messaging': 30,    # Messages kept for 30 days
    'notifications': 30, # Notifications kept for 30 days
    'newsletter': 180,  # Newsletter data kept for 6 months
    
    # Model-specific retention policies (in days)
    'properties.property': 730,  # Properties: 2 years
    'users.user': 2555,          # Users: 7 years (GDPR compliance)
    'leases.lease': 2555,        # Leases: 7 years (legal requirement)
    'leases.paymentschedule': 2555, # Payment records: 7 years
    'maintenance.maintenancerequest': 1095, # Maintenance: 3 years
    'maintenance.workorder': 1095,          # Work orders: 3 years
    'messaging.message': 90,     # Messages: 3 months
    'notifications.notification': 30, # Notifications: 1 month
}

# Static files configuration
static_cfg = get_static_files_config()
STATIC_URL = static_cfg['STATIC_URL']
STATIC_ROOT = static_cfg['STATIC_ROOT']
STATICFILES_DIRS = static_cfg['STATICFILES_DIRS']
STATICFILES_FINDERS = static_cfg['STATICFILES_FINDERS']
STATICFILES_STORAGE = static_cfg.get('STATICFILES_STORAGE', 'django.contrib.staticfiles.storage.StaticFilesStorage')

# Media files configuration
media_cfg = get_media_files_config()
MEDIA_URL = media_cfg['MEDIA_URL']
MEDIA_ROOT = media_cfg['MEDIA_ROOT']
FILE_UPLOAD_MAX_MEMORY_SIZE = media_cfg['FILE_UPLOAD_MAX_MEMORY_SIZE']
DATA_UPLOAD_MAX_MEMORY_SIZE = media_cfg['DATA_UPLOAD_MAX_MEMORY_SIZE']
FILE_UPLOAD_PERMISSIONS = media_cfg['FILE_UPLOAD_PERMISSIONS']
FILE_UPLOAD_DIRECTORY_PERMISSIONS = media_cfg['FILE_UPLOAD_DIRECTORY_PERMISSIONS']

# Email configuration
email_cfg = get_email_config()
EMAIL_BACKEND = email_cfg.get('EMAIL_BACKEND')
DEFAULT_FROM_EMAIL = email_cfg.get('DEFAULT_FROM_EMAIL')
SERVER_EMAIL = email_cfg.get('SERVER_EMAIL')
EMAIL_TIMEOUT = email_cfg.get('EMAIL_TIMEOUT')
if 'EMAIL_HOST' in email_cfg:
    EMAIL_HOST = email_cfg.get('EMAIL_HOST')
    EMAIL_PORT = email_cfg.get('EMAIL_PORT')
    EMAIL_HOST_USER = email_cfg.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = email_cfg.get('EMAIL_HOST_PASSWORD')
    EMAIL_USE_TLS = email_cfg.get('EMAIL_USE_TLS')
    EMAIL_USE_SSL = email_cfg.get('EMAIL_USE_SSL')

# Performance configuration
performance_cfg = get_performance_config()
DATA_UPLOAD_MAX_NUMBER_FIELDS = performance_cfg.get('DATA_UPLOAD_MAX_NUMBER_FIELDS')
DATA_UPLOAD_MAX_MEMORY_SIZE = performance_cfg.get('DATA_UPLOAD_MAX_MEMORY_SIZE')
FILE_UPLOAD_MAX_MEMORY_SIZE = performance_cfg.get('FILE_UPLOAD_MAX_MEMORY_SIZE')
DEFAULT_AUTO_FIELD = performance_cfg.get('DEFAULT_AUTO_FIELD')
USE_THOUSAND_SEPARATOR = performance_cfg.get('USE_THOUSAND_SEPARATOR')
NUMBER_GROUPING = performance_cfg.get('NUMBER_GROUPING')

# Admin configuration
admin_config = get_admin_config()
ADMIN_SITE_HEADER = 'Jaston Administration'
ADMIN_SITE_TITLE = 'Jaston Admin'
ADMIN_INDEX_TITLE = 'Welcome to Jaston Administration'

# Logging configuration
LOGGING = get_logging_config()

# Admin and manager configuration
ADMINS = admin_config['ADMINS']
MANAGERS = admin_config['MANAGERS']
