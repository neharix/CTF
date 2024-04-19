import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from challenge.models import Answer, Challenge
from main.models import User


# Create your views here.
class TeamsStatics:
    def __init__(self, team, points, color):
        self.team = team
        self.points = points
        self.color = color


class UserTeam:
    def __init__(self, challenge, points):
        self.challenge = challenge
        self.points = points


class TeamStatics:
    def __init__(self, user, points, color):
        self.user = user
        self.points = points
        self.color = color


@login_required(login_url="login")
def chart(request):
    if request.user.is_superuser:
        return redirect("home")
    else:
        user_team = request.user.team
        challenges = Challenge.objects.all()

        team_players = User.objects.filter(team__name=user_team.name)
        team_players_data = []

        for player in team_players:
            color = f"rgb({random.randint(1, 255)}, {random.randint(1, 255)}, {random.randint(1, 255)})"
            challenge_points = []
            for challenge in challenges:
                team_answers = Answer.objects.filter(
                    challenge_id=challenge.id,
                    team=user_team.name,
                    username=player.username,
                )
                challenge_points.append(sum([answer.point for answer in team_answers]))
            team_players_data.append(
                TeamStatics(player.username, sum(challenge_points), color)
            )

        user_team_chart = []
        for challenge in challenges:
            team_answers = Answer.objects.filter(
                challenge_id=challenge.id,
                team=user_team.name,
                username=request.user.username,
            )
            user_team_chart.append(
                UserTeam(challenge, sum([answer.point for answer in team_answers]))
            )

        context = {
            "team_players_data": team_players_data,
            "user_team_chart": user_team_chart,
            "user_team": user_team,
        }
        return render(request, "chart/chart.html", context)
