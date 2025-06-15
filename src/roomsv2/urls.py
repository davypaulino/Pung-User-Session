# myapp/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoomGetAPIView,CreateRoomAPIView

urlpatterns = [
    path('rooms/', RoomGetAPIView.as_view(), name='room-list'),
    path('rooms/new-room/', CreateRoomAPIView.as_view(), name='room-create'),
]