from django import forms
from django.forms import ModelForm

from .models import Answer, Challenge, Hint, Quizz


class DateTimeInput(forms.DateTimeInput):
    input_type = "datetime-local"


class AnswerForm(ModelForm):
    class Meta:
        model = Answer
        fields = ["answer"]
