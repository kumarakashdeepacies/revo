from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import kore_investment.users.routing as route

application = ProtocolTypeRouter(
    {
        # (http->django views is added by default)
        "websocket": AuthMiddlewareStack(URLRouter(route.websocket_urlpatterns)),
    }
)
