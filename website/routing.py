# Этот файл вместо обычного urls (который принимает sync запросы), чтобы принимать async запросы
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import chat.routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        #chat routing
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})
