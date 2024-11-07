import json

from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Room, Player, Match, roomTypes

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
            roomName=room_name,
            roomType=room_type,
            maxAmountOfPlayers=max_amount_of_players,
            privateRoom=private_room,
        )

        new_player = Player.objects.create(
            playerName=created_by,
            roomCode=new_room.roomCode,
            matchId=new_room.id,
        )

        new_room.createdBy = new_player.playerId
        new_room.save()

        # if room_type == roomTypes.MATCH:
        #     match = Match.objects.create(
        #         roomCode=new_room.roomCode,
        #         maxAmountOfPlayers=max_amount_of_players #matchStatus
        #     )
        #     new_player.matchId=match.matchId

        return JsonResponse(
            {'roomCode': new_room.roomCode},
            status=201,
            headers={
                'Location': f'/session/rooms/{new_room.roomCode}',
                'userId': new_room.createdBy
            }
        )
        
class AddPlayerToRoomView(View):
    def put(self, request, room_code):
        try:
            data = json.loads(request.body)
            player_name = data.get("playerName")
            if not player_name:
                return JsonResponse({'errorCode': '400', 'message': 'Player name is required'}, status=400)

            room = Room.objects.get(roomCode=room_code)

            if Player.objects.filter(roomCode=room_code).count() >= room.maxAmountOfPlayers:
                return JsonResponse({'errorCode': '403', 'message': 'Room is full'}, status=403)
            
            player = Player.objects.create(
                playerName=player_name,
                roomCode=room_code
                # add profileColor and urlProfileImage
            )
            
            return JsonResponse(
                {},
                status=204,
                headers={
                    'Location': f'/session/rooms/{room_code}',
                    'playerId': player.playerId
                }
            )
        except Room.DoesNotExist:
            return JsonResponse({'errorCode': '404', 'message': 'Room not found'}, status=404)

class RemovePlayerView(View):
    def delete(self, request, room_code, player_id):
        try:
            room = Room.objects.get(roomCode=room_code)
        except Room.DoesNotExist:
            return JsonResponse({'errorCode': '404', 'message': 'Room not found'}, status=404)

        try:
            player = Player.objects.get(playerId=player_id, roomCode=room_code)
        except Player.DoesNotExist:
            return JsonResponse({"errorCode": "404", "message": "Player not found in the room"}, status=404)

        player.delete()

        return JsonResponse(
            {},
            status=204,
            headers={
                'Location': f'/session/rooms/{room_code}/{player_id}',
                'playerId': player_id
            }
        )

class RoomGetView(View):
    def get(self, request):
        try:
            current_page = int(request.GET.get('currentPage', 1))
        except ValueError:
            current_page = 1
        page_size = int(request.GET.get('pageSize', 10))
        filter_label = request.GET.get('filterLabel', '')

        rooms = Room.objects.all().order_by('roomName')
        if filter_label:
            rooms = rooms.filter(
                Q(roomName__icontains=filter_label) | Q(roomCode__icontains=filter_label)
            )

        paginator = Paginator(rooms, page_size)
        try:
            paginated_rooms = paginator.page(current_page)
        except PageNotAnInteger:
            paginated_rooms = paginator.page(1)
        except EmptyPage:
            paginated_rooms = paginator.page(paginator.num_pages)

        data = [
            {
                "roomCode": room.roomCode,
                "amountOfPlayers": room.amountOfPlayers,
                "maxAmountOfPlayers": room.maxAmountOfPlayers,
                "roomName": room.roomName,
                "roomType": room.roomType
            }
            for room in paginated_rooms
        ]

        total_items = rooms.count()
        total_pages = (total_items + page_size - 1) // page_size

        response = {
            "paginatedItems": {
                "currentPage": paginated_rooms.number,
                "pageSize": page_size,
                "nextPage": paginated_rooms.next_page_number() if paginated_rooms.has_next() else None,
                "previousPage": paginated_rooms.previous_page_number() if paginated_rooms.has_previous() else None,
                "hasNextPage": paginated_rooms.has_next(),
                "hasPreviousPage": paginated_rooms.has_previous(),
                "totalPages": total_pages,
                "Data": data
            }
        }

        return JsonResponse(response)

class RoomView(View):

    def delete(self, request, roomCode):
        room = Room.objects.filter(roomCode=roomCode).first()
        if room is None:
            return JsonResponse({}, status=204)
        players = Player.objects.filter(roomCode=roomCode)
        players.delete()
        room.delete()
        return JsonResponse({}, status=200)

    def get(self, request, match_id):
        try:
            match = Room.objects.get(roomCode=match_id)

            players = Player.objects.filter(matchId=match.id)
            players_data = [
                {
                    'id': player.playerId,
                    'name': player.playerName,
                    'profileColor': player.profileColor,
                    'urlProfileImage': player.urlProfileImage,
                    "owner": player.playerId == match.createdBy,
                }
                for player in players
            ]
            return JsonResponse(
                {
                    'matchId': match.id, 
                    'maxAmountOfPlayers': match.maxAmountOfPlayers,
                    'amountOfPlayers': len(players_data),
                    'createdBy': match.createdBy,
                    'players': players_data,
                }
            )
        except Room.DoesNotExist:
            return JsonResponse({'errorCode': '404', 'message': 'Match not found'}, status=404)

class PlayerView(View):
    
    def get(self, request, id):
        player = Player.objects.filter(playerId=id, status=True).first()
        if player is None:
            return JsonResponse({}, status=204)
        
        room = Room.objects.filter(roomCode=player.roomCode).first()
        if room is None or player.status == False:
            return JsonResponse({}, status=204)
        
        return JsonResponse(
            {
                "roomCode": room.roomCode,
                "roomStatus": room.roomStatus,
                "GameCode": room.GameCode,
            },
            status=200,
        )

