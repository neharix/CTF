from django.urls import path

from . import views

urlpatterns = [
    path("", views.admin_tools, name="admin_tools"),
    path("register_tool/", views.register_tools, name="register_tools"),
    path("add_team_form/", views.add_team, name="add_team_form"),
    path("challenges_results/", views.challenge_results, name="challenge_results"),
    path("challenges_results/challenge/<int:challenge_id>/", views.challenge_result),
    path("personal_results/", views.personal_result_nav, name="personal_results"),
    path("personal_results/challenge/<int:challenge_id>/", views.personal_result),
    path("export/", views.export_page, name="export_page"),
    path("export/as_xlsx/", views.get_xlsx_of_challenge, name="get_challenge_xlsx"),
]
