import uuid

from django.db import models
from rooms.models import Room

class GameModel(models.Model):
    id = models.CharField(max_length=64, primary_key=True, editable=False, unique=True, blank=False)
    room = models.ForeignKey(Room, related_name='games', on_delete=models.CASCADE)
    gameWinner = models.CharField(max_length=64, blank=True)
    Status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.id