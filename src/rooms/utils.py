from .models import roomTypes

def get_room_type_range(room_type):
    if room_type == roomTypes.MATCH:
        return [2, 4]
    if room_type == roomTypes.TOURNAMENT:
        return [4, 8, 16]
    raise ValueError(f"Invalid room type: {room_type}")

def validate_field(data, field, field_type, default=None, required=True):
    value = data.get(field, default)
    if required and value is None:
        raise ValueError(f"'{field}' field is mandatory.")
    if not isinstance(value, field_type):
        raise ValueError(f"'{field}' type value is {field_type.__name__}.")
    return value

def validate_amount_players(data, field, field_type, room_type):
    value = data.get(field)
    if value is None:
        raise ValueError(f"'{field}' field is mandatory.")
    if not isinstance(value, field_type):
        raise ValueError(f"'{field}' type value is {field_type.__name__}.")
    range = get_room_type_range(roomTypes(room_type))
    if value not in range:
        raise ValueError(f"'{field}' is not a valid size of players.")
    return value