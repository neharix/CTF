from datetime import date, datetime
from json import dumps
from telnetlib import LOGOUT
from tkinter.tix import CheckList
from urllib import request

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from challenge.models import Challenge, HashResponse

from .models import FlagsFromUnsafety

User = get_user_model()


def home(request):
    now = timezone.now()
    date = now.strftime("%Y-%m-%d %H:%M:%S")
    # challenges = Challenge.objects.all()
    challenges = Challenge.objects.all().filter(
        date_end__gte=date, date_start__lte=date, public=True
    )
    context = {"challenges": challenges}
    return render(request, "index.html", context)


@login_required(login_url="login")
def chart(request):
    if request.user.is_superuser:
        return redirect("home")
    return render(request, "menu/chart.html")


def userLogin(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST" and request.POST.get("su-username") == None:
        username = request.POST.get("username").lower()
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "Ulanyjy ady ulanyjylar hasabynda ýok")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Nädogry ulanyjy ady ýa-da açar sözi")

    context = {}
    return render(request, "menu/login_register.html", context)


def user_logout(request):
    logout(request)
    return redirect("home")


def challenge_list_view(request):
    now = timezone.now()
    date = now.strftime("%Y-%m-%d %H:%M:%S")

    challenges = Challenge.objects.filter(
        date_end__gte=date, date_start__lte=date, public=True
    ).order_by("date_created")

    return render(request, "index.html", {"challenges": challenges})


def return_flag(request, key_words):
    flag = HashResponse.objects.get(
        key_words=key_words, team=request.user.team.name
    ).flag
    return JsonResponse({"what_am_i": flag})
