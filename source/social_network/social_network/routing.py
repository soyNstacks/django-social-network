from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack  
from django.urls import re_path
from chat.consumers import ChatConsumer
from game.consumers import GameConsumer

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter([
            re_path(r'ws/chat/(?P<room_name>\w+)/$', 
                    ChatConsumer.as_asgi()),
            re_path(r'ws/game/(?P<player_name>\w+?)/$', 
                    GameConsumer.as_asgi()),
        ])
    ),
})
     