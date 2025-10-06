"""Django settings for Jaston Real Estate platform."""

from __future__ import annotations
import os
from pathlib import Path
from config.environment import get_env_loader

BASE_DIR = Path(__file__).resolve().parent.parent

# Environment loader
env_loader = get_env_loader()
env_loader.validate_all()

security_config = env_loader.get_security_config()
server_config = env_loader.get_server_config()

SECRET_KEY = security_config.secret_key
DEBUG = security_config.debug
ALLOWED_HOSTS = server_config.allowed_hosts

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
    "django_extensions",
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

if not DEBUG:
    try:
        INSTALLED_APPS.remove('django_extensions')
    except ValueError:
        pass

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "apps.core.middleware.APIErrorMiddleware",
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

# Database & Cache
from config.database import get_database_config
from config.static_files_config import get_static_files_config, get_media_files_config
from config.cache_config import get_cache_config, get_session_config
from config.email_config import get_email_config
from config.performance_config import get_performance_config
from config.admin_config import get_admin_config
from config.logging_config import get_logging_config

DATABASES = get_database_config()

# --- Redis Update: change all ports to 6380 ---
CACHES = get_cache_config()
for cache_name, cache_cfg in CACHES.items():
    location = cache_cfg.get('LOCATION')
    if location and location.startswith('redis://localhost:6379'):
        # replace port 6379 with 6380
        CACHES[cache_name]['LOCATION'] = location.replace('6379', '6380')

# Session
session_cfg = get_session_config()
SESSION_ENGINE = session_cfg.get('SESSION_ENGINE')
SESSION_CACHE_ALIAS = session_cfg.get('SESSION_CACHE_ALIAS')
SESSION_COOKIE_AGE = session_cfg.get('SESSION_COOKIE_AGE')
SESSION_COOKIE_SECURE = session_cfg.get('SESSION_COOKIE_SECURE')
SESSION_COOKIE_HTTPONLY = session_cfg.get('SESSION_COOKIE_HTTPONLY')
SESSION_COOKIE_SAMESITE = session_cfg.get('SESSION_COOKIE_SAMESITE')
SESSION_SAVE_EVERY_REQUEST = session_cfg.get('SESSION_SAVE_EVERY_REQUEST')

# Password validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
from config.deployment import get_internationalization_config
i18n_cfg = get_internationalization_config()
LANGUAGE_CODE = i18n_cfg.get('LANGUAGE_CODE')
TIME_ZONE = i18n_cfg.get('TIME_ZONE')
USE_I18N = i18n_cfg.get('USE_I18N')
USE_TZ = i18n_cfg.get('USE_TZ')
LANGUAGES = i18n_cfg.get('LANGUAGES')
LOCALE_PATHS = i18n_cfg.get('LOCALE_PATHS')

# Security
from config.security_config import (
    get_cors_config, get_csrf_config, get_security_headers_config, get_auth_config
)
cors_cfg = get_cors_config()
CORS_ALLOW_ALL_ORIGINS = cors_cfg.get('CORS_ALLOW_ALL_ORIGINS')
CORS_ALLOW_CREDENTIALS = cors_cfg.get('CORS_ALLOW_CREDENTIALS')
CORS_ALLOWED_ORIGINS = cors_cfg.get('CORS_ALLOWED_ORIGINS')
CORS_ALLOWED_ORIGIN_REGEXES = list(cors_cfg.get('CORS_ALLOWED_ORIGIN_REGEXES') or [])

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

# DRF & Swagger
from config.drf_config import get_drf_config, get_swagger_config
REST_FRAMEWORK = get_drf_config()
swagger_cfg = get_swagger_config()
SWAGGER_SETTINGS = swagger_cfg.get('SWAGGER_SETTINGS')
REDOC_SETTINGS = swagger_cfg.get('REDOC_SETTINGS')

# Channels
from config.channels_config import get_channels_config
channels_cfg = get_channels_config()
CHANNEL_LAYERS = channels_cfg.get('CHANNEL_LAYERS')
# Update Redis port for Channels
for layer_name, layer_cfg in CHANNEL_LAYERS.items():
    hosts = layer_cfg.get('CONFIG', {}).get('hosts', [])
    new_hosts = []
    for host in hosts:
        if isinstance(host, str) and host.startswith('redis://localhost:6379'):
            new_hosts.append(host.replace('6379', '6380'))
        else:
            new_hosts.append(host)
    CHANNEL_LAYERS[layer_name]['CONFIG']['hosts'] = new_hosts
ASGI_APPLICATION = channels_cfg.get('ASGI_APPLICATION', ASGI_APPLICATION)

# Celery
from config.celery_config import get_celery_config
CELERY_CONFIG = get_celery_config()
CELERY_BROKER_URL = CELERY_CONFIG.get('broker_url').replace('6379', '6380')
CELERY_RESULT_BACKEND = CELERY_CONFIG.get('result_backend').replace('6379', '6380')
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
CELERY_BEAT_SCHEDULE = {}
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_TASK_ROUTES = {
    'apps.core.tasks.cleanup_soft_deleted_records': {'queue': 'cleanup'},
    'apps.core.tasks.generate_cleanup_report': {'queue': 'reports'},
    'apps.core.tasks.scheduled_cleanup': {'queue': 'maintenance'},
}
CELERY_TASK_ACKS_LATE = True

# Static & media
static_cfg = get_static_files_config()
STATIC_URL = static_cfg['STATIC_URL']
STATIC_ROOT = static_cfg['STATIC_ROOT']
STATICFILES_DIRS = [d for d in static_cfg['STATICFILES_DIRS'] if Path(d).exists()]
STATICFILES_FINDERS = static_cfg['STATICFILES_FINDERS']
STATICFILES_STORAGE = static_cfg.get('STATICFILES_STORAGE', 'django.contrib.staticfiles.storage.StaticFilesStorage')

media_cfg = get_media_files_config()
MEDIA_URL = media_cfg['MEDIA_URL']
MEDIA_ROOT = media_cfg['MEDIA_ROOT']
FILE_UPLOAD_MAX_MEMORY_SIZE = media_cfg['FILE_UPLOAD_MAX_MEMORY_SIZE']
DATA_UPLOAD_MAX_MEMORY_SIZE = media_cfg['DATA_UPLOAD_MAX_MEMORY_SIZE']
FILE_UPLOAD_PERMISSIONS = media_cfg['FILE_UPLOAD_PERMISSIONS']
FILE_UPLOAD_DIRECTORY_PERMISSIONS = media_cfg['FILE_UPLOAD_DIRECTORY_PERMISSIONS']

# Email
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

# Performance & Admin
performance_cfg = get_performance_config()
DATA_UPLOAD_MAX_NUMBER_FIELDS = performance_cfg.get('DATA_UPLOAD_MAX_NUMBER_FIELDS')
DATA_UPLOAD_MAX_MEMORY_SIZE = performance_cfg.get('DATA_UPLOAD_MAX_MEMORY_SIZE')
FILE_UPLOAD_MAX_MEMORY_SIZE = performance_cfg.get('FILE_UPLOAD_MAX_MEMORY_SIZE')
DEFAULT_AUTO_FIELD = performance_cfg.get('DEFAULT_AUTO_FIELD')
USE_THOUSAND_SEPARATOR = performance_cfg.get('USE_THOUSAND_SEPARATOR')
NUMBER_GROUPING = performance_cfg.get('NUMBER_GROUPING')

admin_config = get_admin_config()
ADMIN_SITE_HEADER = 'Jaston Administration'
ADMIN_SITE_TITLE = 'Jaston Admin'
ADMIN_INDEX_TITLE = 'Welcome to Jaston Administration'

LOGGING = get_logging_config()
ADMINS = admin_config['ADMINS']
MANAGERS = admin_config['MANAGERS']
