from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from .views import chat_room

app_name = "chat"

urlpatterns = [
    path("room/<int:chat_id>/", chat_room),
]
