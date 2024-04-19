from unicodedata import name

from django.urls import path

from . import views

urlpatterns = [
    # path('', views.home, name='home'),
    path("", views.challenge_list_view, name="home"),
    path("running/", views.challenge_list_view_running, name="running"),
    path("search/", views.challenge_list_view_searching, name="search"),
    # path('challenge', views.challenge, name="challenge"),
    path("login/", views.userLogin, name="login"),
    path("user_logout", views.user_logout, name="logout"),
    path("get_flags_from_unsafety/", views.save_flags, name="save_flags"),
    path("hash/decode/<str:key_words>/", views.return_flag),
]
