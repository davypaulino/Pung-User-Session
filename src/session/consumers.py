import json

from channels.generic.websocket import AsyncWebsocketConsumer

class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f"room_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def player_list_update(self, event):
        user_removed = event["userRemoved"]
        await self.send(text_data=json.dumps({
            "type": "player_list_update",
            "userRemoved": user_removed,
        }))

    async def delete_room(self, event):
        await self.send(text_data=json.dumps({
            "type": "delete_room",
        }))

class PlayerScoreConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f"match_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def update_score(self, event):
        await self.send(text_data=json.dumps({
            "type": "update_score",
        }))