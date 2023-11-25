from django.db import models
from django.contrib.auth.models import AbstractUser


class Team(models.Model):
    name = models.CharField(max_length=100)

class User(AbstractUser):
    name = models.CharField(max_length=50, null=True)
    surname = models.CharField(max_length=50, null=True)
    username = models.CharField(max_length=200, unique=True)
    email = models.EmailField(null=True)
    bio = models.TextField(null=True)
    team = models.ForeignKey("Team", on_delete=models.CASCADE, blank=True, null=True)
    avatar = models.ImageField(null=True, default="static/main/images/avatar.svg")

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    
class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
