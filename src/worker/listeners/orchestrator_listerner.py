import redis
import os
import asyncio
import json
import logging

from rooms.models import Match, Room
from asgiref.sync import sync_to_async
from players.models import Player, MatchPlayer

redis_client = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=int(os.environ.get("REDIS_PORT", 6379)), db=0, decode_responses=True)

logger = logging.getLogger(__name__)

class OrchestratorListener:
    def __init__(self):
        self.queue_name = "game-sync-session-queue"
        self.running_tasks = set()

    @sync_to_async
    def increment_stage(self, match):
        if match.room:            
            match.room.stage = match.stage
            match.room.save()

    async def process_game_sync(self, message):
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            return

        match = await Match.objects.filter(id=data["matchId"]).afirst()
        if (match is None):
            return
    
        if data["type"] == "game-created":
            logger.info(f"Stating | {OrchestratorListener.__name__} | game-created | Match {match.id} | Game {match.gameId}.")
            match.gameId = data["gameId"]
            logger.info(f"Finished | {OrchestratorListener.__name__} | game-created | Match {match.id} | Game {match.gameId}.")

        if data["type"] == "game-started":
            logger.info(f"Stating | {OrchestratorListener.__name__} | game-started | Match {match.id} | Game {match.gameId}.")
            match.status = 2
            logger.info(f"Finished | {OrchestratorListener.__name__} | game-started | Match {match.id} | Game {match.gameId}.")

        if data["type"] == "game-over":
            logger.info(f"Stating | {OrchestratorListener.__name__} | game-over | Match {match.id} | Game {match.gameId}.")
            players = await sync_to_async(list)(
                match.players_in_match.select_related("player").all()
            )

            for player in players:
                player_data = next((p for p in data["players"] if p["id"] == player.player.id), None)
                if player_data:
                    player.position = player_data["rank"]
                    await sync_to_async(player.save)()

            match.status = 3
            match.winner = data["winner"]

            
            if (match.nextMatch is not None):
                next_match = await Match.objects.filter(id=match.nextMatch).afirst()
                winner = await Player.objects.filter(id=match.winner).afirst()
                if next_match is not None and winner is not None:
                    await MatchPlayer.objects.acreate(match=next_match, player=winner)

                    as_players = await MatchPlayer.objects.filter(match=next_match).acount()
                    if as_players == 2:
                        next_match.status = 1
                        await self.increment_stage(next_match)
                        await next_match.asave()
            logger.info(f"Finished | {OrchestratorListener.__name__} | game-over | Match {match.id} | Game {match.gameId}.")
        
        await match.asave()

    async def listen(self):
        while True:
            await asyncio.sleep(1)
            message = redis_client.lpop(self.queue_name)
            if message is None:
                continue
            await self.process_game_sync(message)