from rest_framework import serializers
from rooms.models import Room, roomTypes, RoomStatus
from players.models import Player
from rooms.utils import setPlayerColor, setBracketsPosition
import random


class RoomSerializer(serializers.ModelSerializer):
    roomCode = serializers.CharField(source='code', read_only=True)
    numberOfPlayers = serializers.IntegerField(source='amountOfPlayers', read_only=True)
    maxNumberOfPlayers = serializers.IntegerField(source='maxAmountOfPlayers', read_only=True)
    roomName = serializers.CharField(source='name', read_only=True)
    owner = serializers.CharField(source='createdBy', read_only=True)
    type = serializers.ChoiceField(choices=Room.TYPE_CHOICES, read_only=True)
    status = serializers.ChoiceField(choices=Room.STATUS_CHOICES, read_only=True)

    class Meta:
        model = Room
        fields = [
            'id',
            'roomCode',
            'numberOfPlayers',
            'maxNumberOfPlayers',
            'roomName',
            'type',
            'status',
            'privateRoom',
            'stage',
            'owner'
        ]

class RoomCreateSerializer(serializers.ModelSerializer):
    roomName = serializers.CharField(source='name', max_length=100, required=True, allow_blank=False)
    roomType = serializers.ChoiceField(
        choices=Room.TYPE_CHOICES,
        source='type',
        default=roomTypes.SINGLE_PLAYER.value
    )
    maxAmountOfPlayers = serializers.IntegerField(default=2, min_value=1)
    privateRoom = serializers.BooleanField(default=False)

    class Meta:
        model = Room
        fields = [
            'createdBy',
            'roomName',
            'roomType',
            'maxAmountOfPlayers',
            'privateRoom',
        ]
        read_only_fields = ['id', 'code', 'amountOfPlayers', 'status', 'stage', 'createdAt', 'updatedBy', 'updatedAt']

    def validate(self, data):
        room_name = data.get("name")
        if not room_name or not room_name.strip():
            raise serializers.ValidationError({"roomName": "Field 'roomName' is mandatory and cannot be empty."})

        room_type = data.get('type')
        max_players = data.get('maxAmountOfPlayers')

        if room_type == roomTypes.TOURNAMENT.value and max_players > 8:
            raise serializers.ValidationError({"maxAmountOfPlayers": "Tournament rooms cannot have more than 8 players."})

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required to create a room.")

        jwt_user_id = request.user.jwt_id
        jwt_nickname = request.user.nickname
        room_type = validated_data.get('type')

        room = Room.objects.create(**validated_data)

        new_player = Player.objects.create(
            name=jwt_nickname,
            userId=jwt_user_id,
            roomId=room,
            roomCode=room.code,
            profileColor=setPlayerColor(room.code),
            urlProfileImage=f"/assets/img/{random.choice([1, 2])}.png"
        )

        if room_type == roomTypes.TOURNAMENT.value:
            new_player.bracketsPosition = setBracketsPosition(room.code)
            if new_player.bracketsPosition % 2 == 0:
                new_player.profileColor = 1
            else:
                new_player.profileColor = 2
            new_player.save()

        room.createdBy = new_player.name
        room.amountOfPlayers += 1

        if room_type == roomTypes.SINGLE_PLAYER.value:
            Player.objects.create(
                name="Bot",
                userId=str("bot"),
                roomId=room,
                roomCode=room.code,
                profileColor=2,
                urlProfileImage=f"/assets/img/{random.choice([1, 2])}.png"
            )
            room.maxAmountOfPlayers += 1

        room.save()

        return room

    def to_representation(self, instance):
        return {
            'roomCode': instance.code,
            'roomType': instance.type
        }


class PlayerSerializer(serializers.ModelSerializer):
    # 'id' é incluído apenas se o usuário atual for o criador da sala
    # 'name', 'color', 'urlProfileImage', 'owner', 'you' são padrão
    id = serializers.SerializerMethodField()
    owner = serializers.BooleanField(source='is_owner', read_only=True)  # Assumindo que você adicione is_owner no view
    you = serializers.BooleanField(source='is_you', read_only=True)  # Assumindo que você adicione is_you no view

    class Meta:
        model = Player
        fields = ['id', 'name', 'profileColor', 'urlProfileImage', 'owner', 'you']

    def get_id(self, obj):
        # A lógica para ocultar o ID se o usuário não for o owner da sala
        # O self.context['request'] e self.context['room_owner_id'] virão do view
        request_user_id = self.context['request_user_id']
        room_created_by = self.context['room_created_by']
        return obj.id if str(request_user_id) == str(room_created_by) else None


class RoomSerializer(serializers.ModelSerializer):
    players = serializers.SerializerMethodField()
    amountOfPlayers = serializers.SerializerMethodField()
    owner = serializers.BooleanField(source='is_owner_user', read_only=True)  # Assumindo is_owner_user no view
    ownerColor = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = [
            'roomId', 'roomType', 'roomCode', 'roomName',
            'maxAmountOfPlayers', 'amountOfPlayers', 'players',
            'owner', 'ownerColor'
        ]
        # Mapeie os campos do seu modelo para os nomes do JSON de saída, se necessário
        # Ex: room_id no JSON de saída para o campo 'id' do modelo
        extra_kwargs = {
            'id': {'source': 'roomId'},  # Se seu campo no modelo é 'id'
            'type': {'source': 'roomType'},  # Se seu campo no modelo é 'type'
            'code': {'source': 'roomCode'},
            'name': {'source': 'roomName'},
            'max_amount_of_players': {'source': 'maxAmountOfPlayers'},
        }

    def get_players(self, obj):
        # Acessa o usuário logado e o usuário 'RoomOwner' do contexto da view
        request_user_id = self.context['request_user_id']
        room_created_by_id = self.context['room_created_by']

        players = Player.objects.filter(roomCode=obj.code).order_by('profileColor')

        # Passa informações adicionais para o contexto do PlayerSerializer
        player_serializer_context = {
            'request': self.context['request'],
            'request_user_id': request_user_id,
            'room_created_by': room_created_by_id,
        }

        # Converte para um dicionário com a cor como chave, como no seu código original
        players_data = {
            player.profileColor: PlayerSerializer(
                player,
                context=player_serializer_context  # Passa o contexto para o PlayerSerializer
            ).data
            for player in players
        }
        return players_data

    def get_amountOfPlayers(self, obj):
        return Player.objects.filter(roomCode=obj.code).count()

    def get_ownerColor(self, obj):
        # Supondo que você pode buscar o player dono da sala pela room.createdBy
        try:
            owner_player = Player.objects.get(id=obj.createdBy, roomCode=obj.code)
            return owner_player.profileColor
        except Player.DoesNotExist:
            return None  # Ou um valor padrão/erro