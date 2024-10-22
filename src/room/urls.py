from django.urls import path
from .views import RoomStatusView

urlpatterns = [
    path('<str:roomId>/status/', RoomStatusView.as_view(), name='room_status'),
]
