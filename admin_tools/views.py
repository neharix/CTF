import datetime
import os
import random
from io import BytesIO
from pathlib import Path

import pandas as pd
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from challenge.models import Answer, Challenge, Quizz
from main.models import Team, User

from .forms import XlsxForm
from .models import Xlsxes
from .utils import export_xlsx, render_to_pdf


class ChallengeXlsxData:
    def __init__(self, challenge: str, path: str) -> None:
        self.challenge = challenge
        self.path = path


class TeamResults:
    def __init__(self, place, data):
        self.place = place
        self.team = data["team"]
        self.points = data["points"]


class UserResults:
    def __init__(self, place, data):
        self.place = place
        self.user = data["user"]
        self.first_name = data["first_name"]
        self.last_name = data["last_name"]
        self.team = data["team"]
        self.points = data["points"]


def register_tools(request):
    form = XlsxForm()

    if request.user.is_superuser:
        if request.method == "POST":
            form = XlsxForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                media_path = f"./media/{Xlsxes.objects.last().file}"
                dataframe = pd.read_excel(media_path)

                user_data = {
                    "Ady": [],
                    "Familiyasy": [],
                    "Login": [],
                    "Password": [],
                    "Email": [],
                    "Topar": [],
                }
                for i in range(len(dataframe["Ady"])):
                    name = dataframe["Ady"][i].strip()
                    surname = dataframe["Familiyasy"][i].strip()
                    email = dataframe["Email"][i].strip()
                    team = dataframe["Topar"][i].strip()
                    already_in_db = True
                    try:
                        user_object = User.objects.get(
                            first_name=name, last_name=surname
                        )
                    except:
                        already_in_db = False

                    if already_in_db:
                        name = f"{surname} {name}"
                        surname = "Eýýäm maglumat bazasyna bellenilen"
                        email = ""
                        password = ""
                        email = ""
                        team = ""
                        username = ""
                    else:
                        username = (
                            name.lower()
                            + surname.lower()
                            + str(random.randint(1000, 2000))
                        )
                        password = (
                            random.choice([name, surname])
                            + random.choice([name, surname])
                            + str(random.randint(1000, 2000))
                        )
                        try:
                            team = Team.objects.get(name=dataframe["Topar"][i])
                        except ObjectDoesNotExist:
                            team = Team.objects.create(name=dataframe["Topar"][i])
                        User.objects.create_user(
                            username=username,
                            password=password,
                            first_name=name,
                            password_for_usage=password,
                            last_name=surname,
                            email=email,
                            team=team,
                        )

                    user_data["Ady"].append(name)
                    user_data["Familiyasy"].append(surname)
                    user_data["Login"].append(username)
                    user_data["Password"].append(password)
                    user_data["Email"].append(email)
                    user_data["Topar"].append(team)

                export_path = f"/media/exported_xlsx/{Xlsxes.objects.last().file}"
                dataframe = pd.DataFrame(user_data)
                dataframe.to_excel(f".{export_path}")

                request.session["path"] = export_path

                return redirect("register_tools")
        if request.session.get("path"):
            download_path = request.session["path"]
            del request.session["path"]

            context = {"form": form, "path": download_path, "download": True}
            return render(request, "register_tools.html", context)
        else:
            context = {"form": form}
            return render(request, "register_tools.html", context)

    else:
        return redirect("home")


def admin_tools(request):
    if request.user.is_superuser:
        return render(request, "admin_tools.html")
    else:
        return redirect("home")


def export_page(request):
    if request.user.is_superuser:
        return render(request, "export_page.html")
    else:
        return redirect("home")


def add_team(request):
    if request.user.is_superuser:
        if request.method == "POST":
            Team.objects.create(name=request.POST["team"])
            return render(request, "add_team.html")
        else:
            return render(request, "add_team.html")
    else:
        return redirect("home")


def get_xlsx_of_challenge(request):
    data = []
    challenges = Challenge.objects.all()
    for challenge in challenges:
        challenge_answers = {
            "Sorag": [],
            "Jogap beren": [],
            "Topary": [],
            "Berlen bal": [],
            "Jogap berlen sene": [],
        }
        for answer in Answer.objects.filter(challenge_id=challenge.pk):
            if answer.point > 0:
                quizz = Quizz.objects.get(pk=answer.quizz_id)
                user = User.objects.get(username=answer.username)
                challenge_answers["Sorag"].append(quizz.name)
                challenge_answers["Jogap beren"].append(
                    user.last_name.capitalize() + " " + user.first_name.capitalize()
                )
                challenge_answers["Topary"].append(answer.team)
                challenge_answers["Berlen bal"].append(answer.point)
                hour = (
                    int(answer.answered_at.hour) + 5
                    if answer.answered_at.hour + 5 <= 23
                    else (int(answer.answered_at.hour) + 5) % 24
                )
                hour_str = str(hour) if hour >= 10 else f"0{hour}"
                minute_str = (
                    str(answer.answered_at.minute)
                    if answer.answered_at.minute >= 10
                    else f"0{answer.answered_at.minute}"
                )
                second_str = (
                    str(answer.answered_at.second)
                    if answer.answered_at.second >= 10
                    else f"0{answer.answered_at.second}"
                )

                time = f"{hour_str}:{minute_str}:{second_str}"

                challenge_answers["Jogap berlen sene"].append(time)

        dataframe = pd.DataFrame(challenge_answers)
        challenge_slug = challenge.name.lower().replace(" ", "_") + str(
            random.randint(1, 100000)
        )
        dataframe.to_excel(f"./media/exported_xlsx/{challenge_slug}.xlsx")

        data.append(
            ChallengeXlsxData(
                challenge.name,
                f"/media/exported_xlsx/{challenge_slug}.xlsx",
            )
        )

    context = {"data": data}

    return render(request, "xlsx_select.html", context)


def challenge_results(request):
    if request.user.is_superuser or request.user.is_staff:
        challenges = Challenge.objects.all()
        return render(request, "challenge_results.html", {"challenges": challenges})
    else:
        return redirect("home")


def challenge_result(request, challenge_id):
    if request.user.is_superuser or request.user.is_staff:
        by_score_sort = lambda e: e["points"]
        teams = Team.objects.all()
        challenge = Challenge.objects.get(pk=challenge_id)
        results_list = []
        for team in teams:
            points = []
            answers = Answer.objects.filter(challenge_id=challenge.pk, team=team.name)
            for answer in answers:
                points.append(answer.point)
            results_list.append({"team": team.name, "points": sum(points)})
        results_list.sort(key=by_score_sort, reverse=True)
        results = [
            TeamResults(results_list.index(result) + 1, result)
            for result in results_list
        ]

        return render(
            request,
            "challenge_result.html",
            {
                "results": results,
                "challenge": challenge,
            },
        )
    else:
        return redirect("home")


def personal_result_nav(request):
    if request.user.is_superuser or request.user.is_staff:
        challenges = Challenge.objects.all()
        return render(request, "personal_res_nav.html", {"challenges": challenges})
    else:
        return redirect("home")


def personal_result(request, challenge_id):
    if request.user.is_superuser or request.user.is_staff:
        by_score_sort = lambda e: e["points"]
        users = User.objects.filter(is_superuser=False, is_staff=False)
        challenge = Challenge.objects.get(pk=challenge_id)
        results_list = []
        for user in users:
            points = []
            answers = Answer.objects.filter(
                challenge_id=challenge.pk, username=user.username
            )
            for answer in answers:
                points.append(answer.point)
            results_list.append(
                {
                    "user": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "team": user.team.name,
                    "points": sum(points),
                }
            )
        results_list.sort(key=by_score_sort, reverse=True)
        results = [
            UserResults(results_list.index(result) + 1, result)
            for result in results_list
        ]
        return render(
            request,
            "personal_result.html",
            {
                "results": results,
                "challenge": challenge,
            },
        )
    else:
        return redirect("home")


def export_personal_result_as_xlsx(request: HttpRequest, challenge_id: int):
    if request.user.is_superuser or request.user.is_staff:
        by_score_sort = lambda e: e["points"]
        users = User.objects.filter(is_superuser=False, is_staff=False)
        challenge = Challenge.objects.get(pk=challenge_id)
        results_list = []
        dataframe_dict = {"Ady": [], "Familiýasy": [], "Topary": [], "Bal": []}
        for user in users:
            points = []
            answers = Answer.objects.filter(
                challenge_id=challenge.pk, username=user.username
            )
            for answer in answers:
                points.append(answer.point)
            results_list.append(
                {
                    "user": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "team": user.team.name,
                    "points": sum(points),
                }
            )
        results_list.sort(key=by_score_sort, reverse=True)

        for result in results_list:
            dataframe_dict["Ady"].append(result["first_name"])
            dataframe_dict["Familiýasy"].append(result["last_name"])
            dataframe_dict["Topary"].append(result["team"])
            dataframe_dict["Bal"].append(result["points"])
        dataframe = pd.DataFrame(dataframe_dict)
        response = HttpResponse(
            content_type="application/xlsx",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="cybersecurity_team_results.xlsx"'
        )
        with pd.ExcelWriter(response) as writer:
            dataframe.to_excel(writer, sheet_name="sheet1")
        return response
    else:
        return redirect("home")


def export_challenge_result_as_xlsx(request, challenge_id):
    if request.user.is_superuser or request.user.is_staff:
        by_score_sort = lambda e: e["points"]
        teams = Team.objects.all()
        challenge = Challenge.objects.get(pk=challenge_id)
        results_list = []
        dataframe_dict = {"Topar": [], "Bal": []}
        for team in teams:
            points = []
            answers = Answer.objects.filter(challenge_id=challenge.pk, team=team.name)
            for answer in answers:
                points.append(answer.point)
            results_list.append({"team": team.name, "points": sum(points)})
        results_list.sort(key=by_score_sort, reverse=True)
        for result in results_list:
            dataframe_dict["Topar"].append(result["team"])
            dataframe_dict["Bal"].append(result["points"])

        dataframe = pd.DataFrame(dataframe_dict)
        response = HttpResponse(
            content_type="application/xlsx",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="cybersecurity_team_results.xlsx"'
        )
        with pd.ExcelWriter(response) as writer:
            dataframe.to_excel(writer, sheet_name="sheet1")
        return response
    else:
        return redirect("home")


def export_personal_result_as_pdf(request, challenge_id):
    if request.user.is_superuser or request.user.is_staff:
        by_score_sort = lambda e: e["points"]
        users = User.objects.filter(is_superuser=False, is_staff=False)
        challenge = Challenge.objects.get(pk=challenge_id)
        results_list = []
        for user in users:
            points = []
            answers = Answer.objects.filter(
                challenge_id=challenge.pk, username=user.username
            )
            for answer in answers:
                points.append(answer.point)
            results_list.append(
                {
                    "user": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "team": user.team.name,
                    "points": sum(points),
                }
            )
        results_list.sort(key=by_score_sort, reverse=True)
        results = [
            UserResults(results_list.index(result) + 1, result)
            for result in results_list
        ]
        data = {
            "results": results,
            "challenge": challenge,
            "current_year": datetime.datetime.now().year,
        }
        pdf = render_to_pdf("user_results_pdf.html", data)
        return HttpResponse(pdf, content_type="application/pdf")
    else:
        return redirect("home")


def export_challenge_result_as_pdf(request, challenge_id):
    if request.user.is_superuser or request.user.is_staff:
        by_score_sort = lambda e: e["points"]
        teams = Team.objects.all()
        challenge = Challenge.objects.get(pk=challenge_id)
        results_list = []
        for team in teams:
            points = []
            answers = Answer.objects.filter(challenge_id=challenge.pk, team=team.name)
            for answer in answers:
                points.append(answer.point)
            results_list.append({"team": team.name, "points": sum(points)})
        results_list.sort(key=by_score_sort, reverse=True)
        results = [
            TeamResults(results_list.index(result) + 1, result)
            for result in results_list
        ]
        data = {
            "results": results,
            "challenge": challenge,
            "current_year": datetime.datetime.now().year,
        }
        pdf = render_to_pdf("team_results_pdf.html", data)
        return HttpResponse(pdf, content_type="application/pdf")
    else:
        return redirect("home")


def monitoring(request: HttpRequest):
    return render(request, "monitoring.html")
