import json

from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
from .models import Room, Player

class RoomStatusView(View):
    def get(self, request, roomId):
        try:
            room = Room.objects.get(id=roomId)
            return JsonResponse({'status': str(room.roomStatus)})
        except Room.DoesNotExist:
            return JsonResponse({'errorCode': '404', 'message': 'Room status not found'}, status=404)

class CreateRoomView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        created_by = data.get("createdBy")
        room_name = data.get("roomName")
        room_type = data.get("roomType")
        max_amount_of_players = data.get("maxAmountOfPlayers")
        private_room = data.get("privateRoom") == "true"

        if not (created_by and room_name and room_type and max_amount_of_players):
            return JsonResponse({'errorCode': '400', 'message': 'Bad Request'}, status=400)

        try:
            room_type = int(room_type)
            max_amount_of_players = int(max_amount_of_players)
        except ValueError:
            return JsonResponse({'errorCode': '400', 'message': 'Bad Request'}, status=400)

        new_room = Room.objects.create(
            createdBy=created_by,
            roomName=room_name,
            roomType=room_type,
            maxAmountOfPlayers=max_amount_of_players,
            privateRoom=private_room
        )

        response = JsonResponse({'roomCode': new_room.roomCode}, status=201)
        response['Location'] = f'/session/rooms/{new_room.roomCode}'
        response['userId'] = new_room.createdBy

        return response

class MatchPageView(View):
    def get(self, request, room_code):
        try:
            room = Room.objects.get(roomCode=room_code)

            players = Player.objects.filter(roomCode=room.roomCode)
            players_data = [
                {
                    'playerId': player.playerId,
                    'playerName': player.playerName,
                    'profileColor': player.profileColor,
                    'urlProfileImage': player.urlProfileImage
                }
                for player in players
            ]
            return JsonResponse({'roomCode': room.roomCode, 
                                 'maxAmountOfPlayers': room.maxAmountOfPlayers,
                                 'amountOfPlayers': len(players_data),
                                 'createdBy': room.createdBy,
                                 'players': players_data
                                 })
        except Room.DoesNotExist:
            return JsonResponse({'errorCode': '404', 'message': 'Room not found'}, status=404)