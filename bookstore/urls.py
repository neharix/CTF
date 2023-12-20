from django.contrib import admin
from django.urls import path

from .views import book_detail, books_list, login_view, logout_view, search_result

urlpatterns = [
    path("login/", login_view, name="login_view"),
    path("logout/", logout_view, name="logout_view"),
    path("", books_list, name="list"),
    path("<int:pk>/", book_detail, name="detail"),
    path("search/", search_result, name="search_results"),
]
