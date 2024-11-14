from django.urls import path
from .consumers import RoomConsumer

websocket_urlpatterns = [
    path('api/v1/user-session/ws/rooms/<str:room_code>/', RoomConsumer.as_asgi()),
]