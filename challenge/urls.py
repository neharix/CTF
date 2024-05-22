from django.urls import path

from . import views

urlpatterns = [
    path("", views.viewChallenge, name="challenge"),
    path("display_quizzes/<str:pk>/", views.display_quizzes, name="display_quizzes"),
    path("join_challenge/<str:pk>/", views.join_challenge, name="join_challenge"),
    path(
        "register_challenge/<str:pk>/",
        views.register_challenge,
        name="register_challenge",
    ),
    path("play_challenge/<str:pk>/", views.play_challenge, name="play_challenge"),
    path(
        "play_challenge/<str:pk>/play_challenge_quizz/<str:pk1>/",
        views.play_challenge_quizz,
        name="play_challenge_quizz",
    ),
    path("quizz/<int:quizz_id>", views.fake_quizz),
    path("check_answer/", views.check_answer),
]
