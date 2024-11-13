from django.urls import path
from .consumers import RoomConsumer

websocket_urlpatterns = [
    path('api/v1/user-session/ws/rooms/<str:room_code>/', RoomConsumer.as_asgi()),
]


# websocket_urlpatterns = [
#     re_path(r'ws/rooms/(?P<room_code>\w+)/$', RoomConsumer.as_asgi()),
# ]
