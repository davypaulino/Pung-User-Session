from django.urls import path
from .views import PlayerView

urlpatterns = [
    path('<str:id>/', PlayerView.as_view(), name='get-player')
]
