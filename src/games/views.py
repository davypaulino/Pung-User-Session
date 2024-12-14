import redis
import json

from django.http import HttpResponse
from django.views import View
from rooms.models import Room
from rooms.models import RoomStatus
from players.models import Player

redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

class GameView(View):
    def post(self, request, room_code):
        user_id = request.headers.get('X-User-Id')
        if user_id is None:
            return HttpResponse(f"User ID not found", status=400)
        room = Room.objects.filter(code=room_code).first()
        
        if room is None:
            return HttpResponse(f"Room {room_code} not found", status=400)
        if room.players.count() < 2:
            return HttpResponse(f"Minimal amount of players {2}", status=403)
        if room.createdBy != user_id:
            return HttpResponse(f"User {user_id} is not the owner of room {room_code}", status=403)
        
        room.status = RoomStatus.CREATING_GAME
        room.save()
        
        isSinglePlayer = False
        if (room.amountOfPlayers == 1):
            isSinglePlayer = True
        
        message = {
            "type": "create_game",
            "roomId": room.id,
            "isSinglePlayer": isSinglePlayer,
            "ownerId": user_id,
            "players": [
                {
                    "id": player.id,
                    "name": player.name,
                    "color": player.profileColor,
                }
                for player in room.players.all()
            ]
        }

        redis_client.rpush("create-game-queue", json.dumps(message))
        return HttpResponse(f"Game created for room {room_code}", status=201)