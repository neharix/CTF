from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import redirect, render

from .models import Book, ConnectionJournal, CtfTaskObjects


class conObj:
    is_connected = False


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        try:
            bookstore_user = CtfTaskObjects.objects.get(
                username=username, password=password
            )
        except ObjectDoesNotExist:
            return render(
                request,
                "registration/login.html",
                {"error": "Berlen ulanyjy ady ýa-da açar sözi ýalňyş!"},
            )
        if len(ConnectionJournal.objects.filter(username=request.user.username)) == 0:
            ConnectionJournal.objects.create(
                username=request.user.username,
                is_connected=True,
                task_object=bookstore_user,
            )
        else:
            connection = ConnectionJournal.objects.get(username=request.user.username)
            connection.task_object = bookstore_user
            connection.is_connected = True
            connection.save()
        return redirect("list")
    else:
        return render(request, "registration/login.html")


def logout_view(request):
    connection = ConnectionJournal.objects.get(username=request.user.username)
    connection.is_connected = False
    connection.save()
    return redirect("login_view")


def get_connection_info(request):
    try:
        connection = ConnectionJournal.objects.get(username=request.user.username)
    except:
        connection = conObj
    return connection


def books_list(request):
    if get_connection_info(request).is_connected:
        books = Book.objects.all()
        context = {"books": books, "connection": get_connection_info(request)}
        return render(request, "list.html", context)
    else:
        return redirect("login_view")


def book_detail(request, book_id):
    if get_connection_info(request).is_connected:
        book = Book.objects.get(pk=book_id)
        context = {"book": book, "connection": get_connection_info(request)}
        return render(request, "detail.html", context)
    else:
        return redirect("login_view")


def search_result(request):
    if get_connection_info(request).is_connected:
        query = request.GET.get("q")
        books = Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )
        context = {"books": books, "connection": get_connection_info(request)}
        return render(request, "search_results.html", context)
    else:
        return redirect("login_view")
