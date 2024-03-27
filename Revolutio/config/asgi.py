"""
ASGI config for Kore_Investment project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

import django
from django.core.asgi import get_asgi_application

from kore_investment.middleware.websocket_tenant_middleware import TenantMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()


from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import kore_investment.users.routing as route

application = ProtocolTypeRouter(
    {
        # (http->django views is added by default)
        "http": get_asgi_application(),
        "websocket": TenantMiddleware(AuthMiddlewareStack(URLRouter(route.websocket_urlpatterns))),
    }
)
