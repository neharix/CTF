from django.shortcuts import render
from main.models import Team, User
from challenge.models import Challenge, Answer

import random

# Create your views here.
class UserTeam:
    def __init__(self, challenge, points):
        self.challenge = challenge
        self.points = points

class TeamStatics:
    def __init__(self, user, points, color):
        self.user = user
        self.points = points
        self.color = color

def chart(request):
    user_team = request.user.team
    topics = Topic.objects.all()
    data_post = []
    data_challenge = []

    challenges = Challenge.objects.all()

    for topic in topics:
        data_post.append(topic.post_set.all().count())
        # data_challenge.append(topic.challenge_set.all().count())
    
    team_players = User.objects.filter(team__name=user_team.name)
    team_players_data = []

    for player in team_players:
        color = f'rgb({random.randint(1, 255)}, {random.randint(1, 255)}, {random.randint(1, 255)})'
        challenge_points = []
        for challenge in challenges:
            team_answers = Answer.objects.filter(challenge_id=challenge.id, team=user_team.name, username=player.username)
            challenge_points.append(sum([answer.point for answer in team_answers]))
        team_players_data.append(TeamStatics(player.username, sum(challenge_points), color))
        print(challenge_points)

    

    

    user_team_chart = []
    for challenge in challenges:
        
        team_answers = Answer.objects.filter(challenge_id=challenge.id, team=user_team.name, username=request.user.username)
        user_team_chart.append(UserTeam(challenge, sum([answer.point for answer in team_answers])))
        

    data_challenge = [5, 4, 1, 3, 1]
    context = {"team_players_data": team_players_data, "user_team_chart": user_team_chart, 'user_team': user_team,'topics':topics, 'data_post':data_post, 'data_challenge':data_challenge}
    return render(request, 'chart/chart.html', context)