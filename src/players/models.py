import uuid

from django.db import models
from enum import Enum
from rooms.models import Room

class playerColors(Enum):
    RED = 0
    BLUE = 1
    GREEN = 2
    YELLOW = 3

class Player(models.Model):
    id = models.CharField(primary_key=True, max_length=64, editable=False)
    name = models.CharField(max_length=100)
    roomId = models.ForeignKey(Room, related_name='players', on_delete=models.CASCADE)
    roomCode = models.CharField(max_length=64)
    profileColor = models.IntegerField(choices=[
        (1, "Red"),
        (2, "Blue"),
        (3, "Green"),
        (4, "Yellow"),
    ], default=0)
    urlProfileImage = models.CharField(max_length=100)
    score = models.IntegerField(default=0)
    status = models.BooleanField(default=True)
    createdBy = models.CharField(max_length=64)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedBy = models.CharField(max_length=64)
    updatedAt = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name