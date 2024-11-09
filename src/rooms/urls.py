from django.urls import path
from .views import RoomStatusView, CreateRoomView, RoomView, RoomGetView, AddPlayerToRoomView, RemovePlayerView

urlpatterns = [
    path('', RoomGetView.as_view(), name='rooms'),
    path('new-room/', CreateRoomView.as_view(), name='new-room'),
    path('<str:room_code>/delete', RoomView.as_view(), name='rooms'),
    path('<str:room_code>/detail/', RoomView.as_view(), name='match'),
    path('<str:room_code>/status/', RoomStatusView.as_view(), name='room-status'),
    path('<str:room_code>/add-player/', AddPlayerToRoomView.as_view(), name='add-player'),
    path('<str:room_code>/<str:player_id>/remove-player/', RemovePlayerView.as_view(), name='remove-player'),
]