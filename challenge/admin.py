from django.contrib import admin
from xlsxdocument import export_selected

from .models import Answer, Challenge, HashResponse, Hint, Quizz, TrueAnswers

# Register your models here.


class siteAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)


@admin.register(Quizz)
class quizzAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)
    list_display = ["id", "challenge_id", "name", "question", "point", "type_of_quizz"]
    actions = [export_selected]


@admin.register(Answer)
class answerAdmin(admin.ModelAdmin):
    readonly_fields = ("answered_at",)
    actions = [export_selected]


@admin.register(TrueAnswers)
class trueAnswersAdmin(admin.ModelAdmin):
    list_display = ["id", "is_public", "answer", "for_team", "quizz_id"]
    actions = [export_selected]


admin.site.register(Challenge, siteAdmin)
admin.site.register(Hint, siteAdmin)
admin.site.register(HashResponse)
# class NoteAdmin(admin.ModelAdmin):
#     list_filter = ('day_created',)
#     list_display = ('name', 'day_created', 'date_start', 'date_end', 'description')
# admin.site.register(Challenge)
