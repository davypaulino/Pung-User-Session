from django.urls import path
from .views import RoomStatusView, CreateRoomView, MatchPageView, AddPlayerToRoomView, AvailableRoomsView

urlpatterns = [
    path('<str:roomId>/status/', RoomStatusView.as_view(), name='room_status'),
    path('new-room/', CreateRoomView.as_view(), name='new-room'),
    path('match/<str:match_id>/', MatchPageView.as_view(), name='match'),
    path('<str:room_code>/add-player/', AddPlayerToRoomView.as_view(), name='add-player'),
    path('available-rooms/', AvailableRoomsView.as_view(), name='available-rooms')
]
