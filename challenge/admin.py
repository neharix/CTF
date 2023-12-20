from django.contrib import admin

from .models import Answer, Challenge, Hint, Quizz, TrueAnswers

# Register your models here.


class siteAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)


admin.site.register(Challenge, siteAdmin)
admin.site.register(Hint, siteAdmin)
admin.site.register(Quizz, siteAdmin)
admin.site.register(Answer, siteAdmin)
admin.site.register(TrueAnswers)
# class NoteAdmin(admin.ModelAdmin):
#     list_filter = ('day_created',)
#     list_display = ('name', 'day_created', 'date_start', 'date_end', 'description')
# admin.site.register(Challenge)
