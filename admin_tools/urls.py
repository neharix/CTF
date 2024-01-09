from django.urls import path

from . import views

urlpatterns = [
    path("", views.admin_tools, name="admin_tools"),
    path("register_tool/", views.register_tools, name="register_tools"),
    path("add_team_form/", views.add_team, name="add_team_form"),
]
