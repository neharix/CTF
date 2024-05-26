from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render

from .models import ChatRoom


@login_required
def chat_room(request: HttpRequest, chat_id):
    chat = ChatRoom.objects.get(pk=chat_id)
    if request.user in chat.users.all():
        return render(request, "chat_room.html", {"chat": chat})
    else:
        return Http404()
