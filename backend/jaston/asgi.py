"""
ASGI config for jaston project.
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jaston.settings")

# Initialize Django ASGI application safely
django_asgi_app = get_asgi_application()

# Import websocket routes after Django setup
from apps.messaging.routing import websocket_urlpatterns

# Wrap in ProtocolTypeRouter
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
