from django.http import JsonResponse
from django.views import View
from .models import Player
from rooms.models import Room

class PlayerView(View):
    def get(self, request, id):
        player = Player.objects.filter(id=id, status=True).first()
        if player is None:
            return JsonResponse({}, status=204)
        
        room = Room.objects.filter(code=player.roomCode).first()
        if room is None or player.status == False:
            return JsonResponse({}, status=204)
        
        return JsonResponse(
            {
                "roomCode": room.code,
                "roomStatus": room.status,
            },
            status=200,
        )