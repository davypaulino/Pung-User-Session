from django.db import models
from enum import Enum
import hashlib

class roomTypes(Enum):
    MATCH = 0
    TOURNAMENT = 1

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
    id = models.CharField(primary_key=True, max_length=64, editable=False)
    roomName = models.CharField(max_length=100)
    maxAmountOfPlayers = models.IntegerField(default=2)
    amountOfPlayers = models.IntegerField(default=1)
    roomType = models.IntegerField(default=0)
    roomStatus = models.IntegerField(default=0)
    createdBy = models.CharField(max_length=64)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedBy = models.CharField(max_length=64)
    updatedAt = models.DateTimeField(auto_now=True)
    roomCode = models.CharField(max_length=64)
    privateRoom = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.id:
            # Gerar o hash a partir do nome (ou qualquer outra informação que você desejar)
            hash_input = (self.roomName + str(self.roomStatus)).encode('utf-8')
            self.id = hashlib.sha256(hash_input).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.roomName

class Player(models.Model):
    playerId = models.CharField(primary_key=True, max_length=64, editable=False)
    playerName = models.CharField(max_length=100)
    roomCode = models.CharField(max_length=64)
    profileColor = models.IntegerField(default=0)
    urlProfileImage = models.CharField(max_length=100)
    createdBy = models.CharField(max_length=64)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedBy = models.CharField(max_length=64)
    updatedAt = models.DateTimeField(auto_now=True)

class TotalScores(models.Model):
    playerId = models.CharField(primary_key=True, max_length=64, editable=False)
    score = models.IntegerField(default=0)
    createdBy = models.CharField(max_length=64)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedBy = models.CharField(max_length=64)
    updatedAt = models.DateTimeField(auto_now=True)

class Tournament(models.Model):
    tournamentCode = models.CharField(primary_key=True, max_length=64, editable=False)
    numberOfGames = models.IntegerField(default=0)
    amountOfPlayers = models.IntegerField(default=0)
    tournamentWinner = models.CharField(max_length=100)
    createdBy = models.CharField(max_length=64)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedBy = models.CharField(max_length=64)
    updatedAt = models.DateTimeField(auto_now=True)

class TournamentRank(models.Model):
    playerId = models.CharField(primary_key=True, max_length=64, editable=False)
    tournamentCode = models.CharField(max_length=64, editable=False)
    rankPosition = models.IntegerField(default=0)
    numberOfGamesPlayed = models.IntegerField(default=0)