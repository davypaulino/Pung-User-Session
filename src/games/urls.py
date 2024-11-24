from django.urls import path
from .views import GameView

urlpatterns = [
    path('<str:room_code>/new-game/', GameView.as_view(), name='new-game')
]
