"""
ASGI config for chatnotiboard project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from decouple import config
from core.middleware import TokenAuthMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", config("SETTING",cast=str))

application = get_asgi_application()


###############ASGI configuration###########################
import core.routing
from channels.routing import URLRouter,ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
 
 
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(URLRouter(core.routing.websocket_urlpatterns)),
    }
)
