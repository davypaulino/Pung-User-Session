from rest_framework import viewsets
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

        # Construa os cabeçalhos customizados
        # As informações do player foram anexadas temporariamente à instância 'room' no serializer.create()
        # Ou você pode buscá-las do primeiro jogador:
        created_room = serializer.instance
        # Assumindo que o createdBy da Room é o ID do Player criador
        player = Player.objects.filter(id=created_room.createdBy, roomId=created_room).first()

        custom_headers = {
            'Location': f'/rooms/{created_room.code}',
        }
        if player:
            custom_headers['X-User-Id'] = player.id
            custom_headers['X-User-Color'] = player.profileColor

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=custom_headers)
