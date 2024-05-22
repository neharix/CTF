from django.db import models
from parler.models import TranslatableModel, TranslatedFields

# Create your models here.


class Challenge(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=200, null=False, blank=False),
        description=models.TextField(null=True, blank=True),
    )
    owner = models.CharField(max_length=200, null=False, blank=False)
    public = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()


class HashResponse(models.Model):
    url = models.CharField(max_length=200)
    team = models.CharField(max_length=200)
    flag = models.CharField(max_length=200)
    key_words = models.CharField(max_length=200)


class TrueAnswers(models.Model):
    is_public = models.BooleanField(default=False)
    answer = models.CharField(max_length=200)
    for_team = models.CharField(max_length=100, blank=True, null=True)
    quizz_id = models.IntegerField()

    def __str__(self):
        return self.answer


class Quizz(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=200, null=True, blank=True),
        question=models.TextField(null=False, blank=False),
    )
    challenge_id = models.IntegerField()
    point = models.IntegerField()
    type_of_quizz = models.CharField(max_length=200)

    def __str__(self):
        return str(self.challenge_id)


class Hint(TranslatableModel):
    translations = TranslatedFields(content=models.TextField(null=False, blank=False))
    quizz_id = models.IntegerField()
    point = models.IntegerField()
    for_team = models.CharField(max_length=200, default="status:public")

    def __str__(self):
        return str(self.quizz_id)


class Answer(models.Model):
    username = models.CharField(max_length=20, null=True, blank=True)
    team = models.CharField(max_length=20, null=True, blank=True)
    challenge_id = models.IntegerField()
    quizz_id = models.IntegerField()
    answer = models.TextField(null=False, blank=False)
    point = models.IntegerField()
    status = models.CharField(max_length=10)
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
