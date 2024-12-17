import redis
import os
import asyncio
import json

from rooms.models import Match, Room
from asgiref.sync import sync_to_async
from players.models import Player, MatchPlayer

redis_client = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=int(os.environ.get("REDIS_PORT", 6379)), db=0, decode_responses=True)

class OrchestratorListener:
    def __init__(self):
        self.queue_name = "game-sync-session-queue"
        self.running_tasks = set()

    async def process_game_sync(self, message):
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            return

        match = await Match.objects.filter(id=data["matchId"]).afirst()
        if (match is None):
            return
    
        if data["type"] == "game-created":
            match.gameId = data["gameId"]

        if data["type"] == "game-started":
            match.status = 1

        if data["type"] == "game-over":
            players = await sync_to_async(list)(
                match.players_in_match.select_related("player").all()
            )

            for player in players:
                player_data = next((p for p in data["players"] if p["id"] == player.player.id), None)
                if player_data:
                    player.position = player_data["rank"]
                    await sync_to_async(player.save)()

            match.status = 2
            match.winner = data["winner"]
            await sync_to_async(match.save)()

        await match.asave()

    async def listen(self):
        while True:
            await asyncio.sleep(1)
            message = redis_client.lpop(self.queue_name)
            if message is None:
                continue
            await self.process_game_sync(message)