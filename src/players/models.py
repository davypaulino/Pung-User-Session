import uuid

from django.db import models

class Player(models.Model):
    id = models.CharField(primary_key=True, max_length=64, editable=False)
    name = models.CharField(max_length=100)
    roomCode = models.CharField(max_length=64)
    profileColor = models.IntegerField(default=0)
    urlProfileImage = models.CharField(max_length=100)
    status = models.BooleanField(default=True)
    createdBy = models.CharField(max_length=64)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedBy = models.CharField(max_length=64)
    updatedAt = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4().int)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name