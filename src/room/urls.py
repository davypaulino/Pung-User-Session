from django.urls import path
from .views import RoomStatusView, CreateRoomView

urlpatterns = [
    path('<str:roomId>/status/', RoomStatusView.as_view(), name='room_status'),
    path('new-room', CreateRoomView.as_view(), name='new-room'),
]
