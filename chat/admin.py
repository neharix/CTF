from django.contrib import admin

from .models import ChatRoom


@admin.register(ChatRoom)
class chatAdmin(admin.ModelAdmin):
    list_display = ["id"]
