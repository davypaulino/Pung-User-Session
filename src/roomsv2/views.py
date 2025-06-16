from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django.db.models import Q, F
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rooms.models import Room, RoomStatus
from players.models import Player
from .serializers import RoomSerializer, RoomCreateSerializer
from .pagination import CustomRoomPagination

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class RoomGetAPIView(ListAPIView):
    serializer_class = RoomSerializer
    pagination_class = CustomRoomPagination
    filter_backends = [SearchFilter]
    renderer_classes = [JSONRenderer]

    search_fields = ['name', 'code']

    def get_queryset(self):
        queryset = Room.objects.filter(
            privateRoom=False,
            amountOfPlayers__lt=F('maxAmountOfPlayers'),
            status__lt=RoomStatus.READY_FOR_START.value
        ).order_by('name')

        return queryset


class CreateRoomAPIView(CreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)

        created_room = serializer.instance
        jwt_user_id = request.user.jwt_id
        player = Player.objects.filter(userId=jwt_user_id, roomId=created_room).first()

        custom_headers = {
            'Location': f'/rooms/{created_room.code}',
        }
        if player:
            custom_headers['X-User-Id'] = player.id
            custom_headers['X-User-Color'] = player.profileColor

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=custom_headers)

class RoomDetailView(APIView):
    # Se você tiver autenticação e permissões configuradas no settings.py,
    # elas serão aplicadas automaticamente aqui.
    # Ex: authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, room_code):
        try:
            user_id = request.user.id
            room = Room.objects.get(code=room_code)
        except Room.DoesNotExist:
            return Response({'errorCode': '404', 'message': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)

        if room.type == 1: # Check is Tournament
            return Response({'errorCode': '400', 'message': 'Bad request - Invalid room type'}, status=status.HTTP_400_BAD_REQUEST)

        current_user_player_instance = Player.objects.filter(roomCode=room.code, id=user_id).first()
        if not current_user_player_instance:
            return Response({'errorCode': '403', 'message': 'Forbidden - User not in room'}, status=status.HTTP_403_FORBIDDEN)

        # 4. Preparar contexto para o serializer
        # Passamos o user_id do request e o createdBy da sala para o serializer
        # para que a lógica de ocultar 'id' e 'owner' possa ser aplicada lá.
        serializer_context = {
            'request': request, # Passa o request completo para acesso no serializer
            'request_user_id': user_id,
            'room_created_by': room.createdBy, # Assumindo que room.createdBy é o ID do Player que criou a sala
        }

        # Adicionar propriedades dinâmicas ao objeto room ANTES de serializar
        # Estes são usados pelos SerializerMethodField no RoomSerializer
        room.is_owner_user = (str(user_id) == str(room.createdBy)) # Se o user_id atual é o owner da sala
        # As propriedades 'is_owner' e 'is_you' para Player são calculadas dentro do PlayerSerializer

        serializer = RoomSerializer(room, context=serializer_context)
        return Response(serializer.data, status=status.HTTP_200_OK)