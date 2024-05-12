from django.urls import path

from . import views

urlpatterns = [
    # path('', views.home, name='home'),
    path("", views.challenge_list_view, name="home"),
    path("login/", views.userLogin, name="login"),
    path("user_logout", views.user_logout, name="logout"),
    path("hash/decode/<str:key_words>/", views.return_flag),
]
