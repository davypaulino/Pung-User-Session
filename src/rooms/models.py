import uuid

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from enum import Enum

def generate_unique_code(model):
    while True:
        code = str(uuid.uuid4().int)[:8]
        if not model.objects.filter(roomCode=code).exists():
            return code

class roomTypes(Enum):
    MATCH = 0
    TOURNAMENT = 1
    SINGLE_PLAYER = 2

class RoomStatus(Enum):
    CREATING_ROOM = 0
    ROOM_CREATED = 1
    WAITING_MINIMAL_AMOUNT_OF_PLAYERS = 2
    READY_FOR_START = 3
    CREATING_GAME = 4
    GAME_CREATED = 5
    GAME_STARTED = 6
    GAME_ENDED = 7

class Room(models.Model):
    TYPE_CHOICES = [
        (0, "Match"),
        (1, "Tournament"),
    ]

    STATUS_CHOICES = [
        (0, "Creating Room"),
        (1, "Room Created"),
        (2, "Waiting Minimal Amount of Players"),
        (3, "Ready for Start"),
        (4, "Creating Game"),
        (5, "Game Created"),
        (6, "Game Started"),
        (7, "Game Ended"),
    ]

    id = models.CharField(primary_key=True, max_length=64, editable=False)
    code = models.CharField(max_length=64)
    name = models.CharField(max_length=100)
    maxAmountOfPlayers = models.IntegerField(default=2)
    amountOfPlayers = models.IntegerField(default=0)
    type = models.IntegerField(choices=TYPE_CHOICES, default=0)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    privateRoom = models.BooleanField(default=False)
    createdBy = models.CharField(max_length=64)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedBy = models.CharField(max_length=64)
    updatedAt = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if isinstance(self.status, RoomStatus):
            self.status = self.status.value 
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.code:
            self.code = str(self.id)[:8]
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name

# class Match(models.Model):
#     matchId = models.CharField(primary_key=True, max_length=64, editable=False)
#     roomCode = models.CharField(max_length=64)
#     maxAmountOfPlayers = models.IntegerField(default=1)
#     amountOfPlayers = models.IntegerField(default=1)
#     matchStatus = models.IntegerField(default=0)
#     matchWinner = models.CharField(max_length=100)
#     createdBy = models.CharField(max_length=64)
#     createdAt = models.DateTimeField(auto_now_add=True)
#     updatedBy = models.CharField(max_length=64)
#     updatedAt = models.DateTimeField(auto_now=True)

#     def save(self, *args, **kwargs):
#         if not self.matchId:
#             self.matchId = str(uuid.uuid4().int)
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.matchId

# class TotalScores(models.Model):
#     playerId = models.CharField(primary_key=True, max_length=64, editable=False)
#     score = models.IntegerField(default=0)
#     createdBy = models.CharField(max_length=64)
#     createdAt = models.DateTimeField(auto_now_add=True)
#     updatedBy = models.CharField(max_length=64)
#     updatedAt = models.DateTimeField(auto_now=True)

# class Tournament(models.Model):
#     tournamentCode = models.CharField(primary_key=True, max_length=64, editable=False)
#     numberOfGames = models.IntegerField(default=0)
#     amountOfPlayers = models.IntegerField(default=0)
#     tournamentWinner = models.CharField(max_length=100)
#     createdBy = models.CharField(max_length=64)
#     createdAt = models.DateTimeField(auto_now_add=True)
#     updatedBy = models.CharField(max_length=64)
#     updatedAt = models.DateTimeField(auto_now=True)

# class TournamentRank(models.Model):
#     playerId = models.CharField(primary_key=True, max_length=64, editable=False)
#     tournamentCode = models.CharField(max_length=64, editable=False)
#     rankPosition = models.IntegerField(default=0)
#     numberOfGamesPlayed = models.IntegerField(default=0)