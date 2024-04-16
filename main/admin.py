from django.contrib import admin

from .models import File, FlagsFromUnsafety, Team, User

# Register your models here.
admin.site.register(User)
admin.site.register(Team)
admin.site.register(File)
admin.site.register(FlagsFromUnsafety)
