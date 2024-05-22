from django.contrib import admin
from xlsxdocument import export_selected

from .models import File, Team, User


@admin.register(File)
class fileAdmin(admin.ModelAdmin):
    list_display = ["id", "file", "quizz_id", "for_team"]


@admin.register(User)
class fileAdmin(admin.ModelAdmin):
    list_display = ["id", "username", "team", "first_name", "last_name"]
    actions = [export_selected]


admin.site.register(Team)
