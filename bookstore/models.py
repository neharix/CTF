# Create your models here.
from django.db import models


class CtfTaskObjects(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    for_quizz = models.IntegerField()

    def __str__(self):
        return self.username


class UserDatas(models.Model):
    flag = models.CharField(max_length=100)
    for_team = models.CharField(max_length=100)

    def __str__(self):
        return self.for_team


class ConnectionJournal(models.Model):
    task_object = models.ForeignKey("CtfTaskObjects", on_delete=models.PROTECT)
    username = models.CharField(max_length=100)
    is_connected = models.BooleanField()

    def __str__(self):
        return (
            f"{self.username} is connected"
            if self.is_connected
            else f"{self.username} isn't connected"
        )


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    price = models.FloatField(null=True, blank=True)
    image = models.ImageField(upload_to="image/")
    follow_author = models.TextField(null=True, blank=True)
    book_available = models.BooleanField(default=False)

    def __str__(self):
        return self.title
