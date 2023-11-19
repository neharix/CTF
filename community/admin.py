from django.contrib import admin

from .models import Post, Topic, Comment, User, Note, Team

# Register your models here.
admin.site.register(Post)
admin.site.register(Topic)
admin.site.register(Comment)
admin.site.register(User)
admin.site.register(Team)

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_filter = ('user',)
    list_display = ('user', 'date', 'content',)
# admin.site.register(Note)