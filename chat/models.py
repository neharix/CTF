from django.db import models

from main.models import User


class ChatRoom(models.Model):
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(User)
