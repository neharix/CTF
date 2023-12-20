from django.contrib import admin

from .models import ConnectionJournal, CtfTaskObjects, UserDatas

admin.site.register(UserDatas)
admin.site.register(ConnectionJournal)
admin.site.register(CtfTaskObjects)
