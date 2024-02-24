from django.urls import path

from . import views

urlpatterns = [
    path("", views.admin_tools, name="admin_tools"),
    path("register_tool/", views.register_tools, name="register_tools"),
    path("add_team_form/", views.add_team, name="add_team_form"),
    path("challenges_results/", views.challenge_results, name="challenge_results"),
    path("challenges_results/challenge/<int:challenge_id>/", views.challenge_result),
]
