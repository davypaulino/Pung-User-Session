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

class PlayersInfoView(View):
    def get(self, request, room_code):
        players = Player.objects.filter(roomCode=room_code)
        if players is None:
            return JsonResponse({}, status=204)
        players_data = [
            {
                'name': player.name,
                'profileColor': player.profileColor,
                'urlProfileImage': player.urlProfileImage,
                'score': player.score,
            }
            for player in players
        ]
        return JsonResponse(
            {
                "players": players_data,
            },
            status=200,
        )

class UpdatePlayerScoreView(View):
    def post(self, request, room_code, player_color):
        player = Player.objects.filter(roomCode=room_code, profileColor=player_color).first
        if player is None:
            return JsonResponse({}, status=204)
        player.score += 1
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
        f"match_{room_code}",
        {
            "type": "update_score",
        }
    )