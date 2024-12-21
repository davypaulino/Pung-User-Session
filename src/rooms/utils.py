import random

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import roomTypes, Room, Match
from players.models import Player, playerColors, MatchPlayer

def get_room_type_range(room_type):
    if room_type == roomTypes.MATCH:
        return [2, 4]
    if room_type == roomTypes.TOURNAMENT:
        return [4, 8, 16]
    if room_type == roomTypes.SINGLE_PLAYER:
        return [1]
    raise ValueError(f"Invalid room type: {room_type}")

def validate_field(data, field, field_type, default=None, required=True):
    value = data.get(field, default)
    if required and value is None:
        raise ValueError(f"'{field}' field is mandatory.")
    if not isinstance(value, field_type):
        raise ValueError(f"'{field}' type value is {field_type.__name__}.")
    return value

def validate_name_field(data, field, required=True):
    value = data.get(field, "Senhor Bolinha")
    if required and value is None:
        raise ValueError(f"'{field}' field is mandatory.")
    if not isinstance(value, str):
        raise ValueError(f"'{field}' type value is {str.__name__}.")
    if len(value) < 3 or len(value) > 100:
        raise ValueError(f"'{field}' value must have between 3 and 100 characters.")
    return value

def validate_integer_field(data, field, default=None, required=True):
    value = data.get(field, default)
    if required and value is None:
        raise ValueError(f"'{field}' field is mandatory.")
    if isinstance(value, str):
        try:
            value = int(value)
        except ValueError:
            raise ValueError(f"'{field}' value must be an integer or a string representing an integer.")
    if not isinstance(value, int):
        raise ValueError(f"'{field}' type value is {int.__name__}.")
    return value


def validate_amount_players(data, field, field_type, room_type):
    value = data.get(field)
    if value is None:
        raise ValueError(f"'{field}' field is mandatory.")
    if isinstance(value, str):
        try:
            value = int(value)
        except ValueError:
            raise ValueError(f"'{field}' value must be an integer or a string representing an integer.")
    if not isinstance(value, field_type):
        raise ValueError(f"'{field}' type value is {field_type.__name__}.")
    range = get_room_type_range(roomTypes(room_type))
    if value not in range:
        raise ValueError(f"'{field}' is not a valid size of players.")
    return value

def setPlayerColor(room_code):
    room = Room.objects.filter(code=room_code).first()
    profileColor = 0
    used_colors = Player.objects.filter(roomCode=room_code).values_list('profileColor', flat=True)
    all_colors = {color.value for color in playerColors}
    available_colors = all_colors - set(used_colors)
    if available_colors:
        profileColor = available_colors.pop()
    return profileColor

def setBracketsPosition(room_code):
    room = Room.objects.filter(code=room_code).first()
    used_positions = room.players.values_list('bracketsPosition', flat=True)
    used_positions_list = list(used_positions)

    avaliable_positions_list = list(filter(lambda x: x not in used_positions_list, list(range(1,room.maxAmountOfPlayers + 1))))
    return random.choice(avaliable_positions_list)

def createPreviousMatchesTournament(room, stage, nextMatch, position):
        if stage < 1:
            return
        numberOfRounds = (room.maxAmountOfPlayers // 2)
        for i in range(1, 3):
            match = Match.objects.create(
                room=room,
                stage=stage,
                status=0,
                position=position - i,
                nextMatch=nextMatch,
            )
            if numberOfRounds == 3 or (numberOfRounds == 4 and stage == 3):
                if i == 1:
                    position -= 2
                else:
                    position -= 4
            elif numberOfRounds == 4 and stage == 2:
                if position == 13:
                    if i == 1:
                        position = 9
                    else:
                        position = 7
                elif position == 11:
                    if i == 1:
                        position = 5
                    else:
                        position = 3

            createPreviousMatchesTournament(room, stage - 1, match.id, position)

def setFirstRound(room):
    playerNumber = 1
    for matchPosition in range(1, 3):
        match = Match.objects.filter(room=room, stage=1, position=matchPosition).first()
        player_one = Player.objects.filter(roomId=room, bracketsPosition=playerNumber).first()
        player_two = Player.objects.filter(roomId=room, bracketsPosition=playerNumber + 1).first()
        MatchPlayer.objects.create(match=match, player=player_one)
        MatchPlayer.objects.create(match=match, player=player_two)
        playerNumber += 2

# def setNextRound(room, nextRound):
#     firstMatchPosition = maxAmountOfPlayers
#     for i in range(1, nextRound):
#         firstMatchPosition -= maxAmountOfPlayers // (2 ** i)
#     for matchPosition in range(firstMatchPosition, room.maxAmountOfPlayers / 2 ** (nextRound - 1)):
#         match = Match.objects.filter(room=room, stage=nextRound - 1, position=matchPosition).first()
#         winner = Player.objects.filter(id=match.winner, roomId=room).first()
#         nextMatch = Match.objects.filter(room=room, stage=nextRound, id=match.nextMatch).first()
#         MatchPlayer.objects.create(match=nextMatch, player=winner)

def createTournamentMatches(room):
    numberOfRounds = (room.maxAmountOfPlayers // 2)
    position = room.maxAmountOfPlayers - 1
    finalMatch = Match.objects.create(
        room=room,
        stage=numberOfRounds,
        status=0,
        position=position,
        nextMatch=None,
    )

    createPreviousMatchesTournament(room, numberOfRounds - 1, finalMatch.id, position)

    setFirstRound(room)