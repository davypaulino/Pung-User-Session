import json

from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
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
            createdBy=created_by,
            roomName=room_name,
            roomType=room_type,
            maxAmountOfPlayers=max_amount_of_players,
            privateRoom=private_room
        )

        if room_type == roomTypes.MATCH:
            Match.objects.create(
                roomCode=new_room.roomCode,
                maxAmountOfPlayers=max_amount_of_players #matchStatus
            )

        return JsonResponse(
            {'roomCode': new_room.roomCode},
            status=201,
            headers={
                'Location': f'/room/?room={new_room.roomCode}',
                'userId': new_room.createdBy
            }
        )

class MatchPageView(View):
    def get(self, request, match_id):
        try:
            match = Match.objects.get(matchId=match_id)

            players = Player.objects.filter(matchId=match.matchId)
            players_data = [
                {
                    'playerId': player.playerId,
                    'playerName': player.playerName,
                    'profileColor': player.profileColor,
                    'urlProfileImage': player.urlProfileImage
                }
                for player in players
            ]
            return JsonResponse(
                {
                    'matchId': match.matchId, 
                    'maxAmountOfPlayers': match.maxAmountOfPlayers,
                    'amountOfPlayers': len(players_data),
                    'createdBy': match.createdBy,
                    'players': players_data
                }
            )
        except Room.DoesNotExist:
            return JsonResponse({'errorCode': '404', 'message': 'Match not found'}, status=404)
        
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

class AvailableRoomsView(View):
    def get(self, request):
        try:
            current_page = int(request.GET.get('currentPage', 1))
        except ValueError:
            current_page = 1
        page_size = int(request.GET.get('pageSize', 10))
        filter_label = request.GET.get('filterLabel', '')

        rooms = Room.objects.all()
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

        response = {
            "paginatedItems": {
                "currentPage": paginated_rooms.number,
                "pageSize": page_size,
                "nextPage": paginated_rooms.next_page_number() if paginated_rooms.has_next() else None,
                "previousPage": paginated_rooms.previous_page_number() if paginated_rooms.has_previous() else None,
                "hasNextPage": paginated_rooms.has_next(),
                "hasPreviousPage": paginated_rooms.has_previous(),
                "Data": data
            }
        }

        return JsonResponse(response)