from django.urls import path
from .views import RoomStatusView, CreateRoomView, AddPlayerToRoomView, RoomView, RoomGetView, RemovePlayerView, PlayerView

urlpatterns = [
    path('rooms/', RoomGetView.as_view(), name='rooms'),
    path('rooms/new-room/', CreateRoomView.as_view(), name='new-room'),
    path('rooms/<str:roomCode>/delete', RoomView.as_view(), name='rooms'),
    path('rooms/<str:match_id>/detail/', RoomView.as_view(), name='match'),
    path('rooms/<str:roomId>/status/', RoomStatusView.as_view(), name='room_status'),
    path('rooms/<str:room_code>/add-player/', AddPlayerToRoomView.as_view(), name='add-player'),
    path('rooms/remove-player/<str:room_code>/<str:player_id>/', RemovePlayerView.as_view(), name='remove-player'),
    path('players/<str:id>/', PlayerView.as_view(), name='get-player')
]
