from django.urls import path
from .views import RoomStatusView, CreateRoomView, MatchPageView

urlpatterns = [
    path('<str:roomId>/status/', RoomStatusView.as_view(), name='room_status'),
    path('new-room/', CreateRoomView.as_view(), name='new-room'),
    path('match/<str:room_code>', MatchPageView.as_view(), name='match')
]
