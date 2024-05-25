from django.contrib import admin
from django.http import HttpRequest
from parler.admin import TranslatableAdmin
from xlsxdocument import export_selected

from .models import Faq, File, Team, User


@admin.register(File)
class fileAdmin(admin.ModelAdmin):
    list_display = ["id", "file", "quizz_id", "for_team"]


@admin.register(Faq)
class FaqAdmin(TranslatableAdmin):
    list_display = ["id", "question", "answer"]

    def get_prepopulated_fields(
        self, request: HttpRequest, obj=None
    ) -> dict[str, tuple[str]]:
        return {"question": ("question",), "answer": ("answer",)}


@admin.register(User)
class fileAdmin(admin.ModelAdmin):
    list_display = ["id", "username", "team", "first_name", "last_name"]
    actions = [export_selected]


admin.site.register(Team)
