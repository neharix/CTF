from django.contrib.auth.models import AbstractUser
from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class User(AbstractUser):
    name = models.CharField(max_length=50, null=True)
    surname = models.CharField(max_length=50, null=True)
    username = models.CharField(max_length=200, unique=True)
    email = models.EmailField(null=True)
    bio = models.TextField(null=True)
    password_for_usage = models.CharField(max_length=200)
    team = models.ForeignKey("Team", on_delete=models.CASCADE, blank=True, null=True)
    avatar = models.ImageField(null=True, default="static/main/images/avatar.svg")

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []


class File(models.Model):
    file = models.FileField(upload_to="files/")
    quizz_id = models.IntegerField()
    for_team = models.CharField(max_length=50, default="status:public")

    def __str__(self):
        return f"Quizz {self.quizz_id} file"


class FlagsFromUnsafety(models.Model):
    flag = models.CharField(max_length=200)
