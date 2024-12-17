import random

from .models import roomTypes, Room
from players.models import Player, playerColors

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