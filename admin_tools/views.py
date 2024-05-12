import random
from pathlib import Path

import pandas as pd
from borb.io.read.types import Decimal
from borb.pdf.canvas.color.color import X11Color
from borb.pdf.canvas.font.simple_font.true_type_font import TrueTypeFont
from borb.pdf.canvas.layout.page_layout.single_column_layout_with_overflow import (
    SingleColumnLayout,
)
from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable
from borb.pdf.canvas.layout.table.table import TableCell
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.document.document import Document
from borb.pdf.page.page import Page
from borb.pdf.pdf import PDF
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render

from challenge.models import Answer, Challenge, Quizz
from main.models import Team, User

from .forms import XlsxForm
from .models import Xlsxes


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
                    name = dataframe["Ady"][i]
                    surname = dataframe["Familiyasy"][i]
                    email = dataframe["Email"][i]
                    team = dataframe["Topar"][i]
                    already_in_db = True
                    try:
                        user_object = User.objects.get(name=name, surname=surname)
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
                            return render(
                                request,
                                "register_tools.html",
                                {
                                    "error": "Tablisadaky toparlar maglumat bazasyna girizilmedik! Administrasiýa saýtynda toparlary registrirläň!",
                                    "form": XlsxForm(),
                                },
                            )
                        User.objects.create_user(
                            username=username,
                            password=password,
                            name=name,
                            password_for_usage=password,
                            surname=surname,
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
                    user.surname.capitalize() + " " + user.name.capitalize()
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
        dataframe_dict = {"Topar": [], "Bal": []}
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

        for result in results_list:
            dataframe_dict["Topar"].append(result["team"])
            dataframe_dict["Bal"].append(result["points"])

        challenge_slug = challenge.name.lower().replace(" ", "_") + str(
            random.randint(1, 100000)
        )
        pd.DataFrame(dataframe_dict).to_excel(
            f"./media/exported_xlsx/{challenge_slug}_teams.xlsx"
        )

        path = str(settings.BASE_DIR).replace("\\", "/")
        font = TrueTypeFont().true_type_font_from_file(
            Path(path + "/admin_tools/static/fonts/VelaSans-Regular.ttf")
        )
        document = Document()
        page = Page()
        layout = SingleColumnLayout(page)
        layout.add(
            Paragraph(
                f'Toparlaryň "{challenge.name}" ýarysy boýunca netijeleri',
                font=font,
                font_size=Decimal(20),
            )
        )
        if len(results_list) > 20:
            row_count = 21
        else:
            row_count = len(results_list) + 1
        layout.add(
            Paragraph(
                f"Top-20" if row_count == 21 else f"",
                font=font,
                font_size=Decimal(14),
            )
        )
        table = (
            FixedColumnWidthTable(
                number_of_columns=3,
                number_of_rows=row_count,
                column_widths=[Decimal(1), Decimal(2), Decimal(1)],
            )
            .add(
                Paragraph(
                    "Ýer",
                    font=font,
                )
            )
            .add(
                Paragraph(
                    "Topar",
                    font=font,
                )
            )
            .add(
                Paragraph(
                    "Bal",
                    font=font,
                )
            )
        )
        sh = 0
        for result in results_list:
            if sh == 20:
                break
            sh += 1
            table.add(Paragraph(str(sh), font=font))
            table.add(Paragraph(result["team"], font=font))
            table.add(Paragraph(str(result["points"]), font=font))

        layout.add(
            table.set_padding_on_all_cells(
                Decimal(3), Decimal(3), Decimal(3), Decimal(3)
            )
        )

        document.add_page(page)

        with open(
            path + f"/media/exported_pdf/{challenge_slug}_team.pdf", "wb"
        ) as pdf_file_handle:
            PDF.dumps(pdf_file_handle, document)

        return render(
            request,
            "challenge_result.html",
            {
                "results": results,
                "challenge": challenge,
                "xlsx_path": f"/media/exported_xlsx/{challenge_slug}_teams.xlsx",
                "pdf_path": f"/media/exported_pdf/{challenge_slug}_team.pdf",
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
                    "first_name": user.name,
                    "last_name": user.surname,
                    "team": user.team.name,
                    "points": sum(points),
                }
            )
        results_list.sort(key=by_score_sort, reverse=True)
        results = [
            UserResults(results_list.index(result) + 1, result)
            for result in results_list
        ]
        for result in results_list:
            dataframe_dict["Ady"].append(result["first_name"])
            dataframe_dict["Familiýasy"].append(result["last_name"])
            dataframe_dict["Topary"].append(result["team"])
            dataframe_dict["Bal"].append(result["points"])

        challenge_slug = challenge.name.lower().replace(" ", "_") + str(
            random.randint(1, 100000)
        )
        pd.DataFrame(dataframe_dict).to_excel(
            f"./media/exported_xlsx/{challenge_slug}_users.xlsx"
        )
        path = str(settings.BASE_DIR).replace("\\", "/")
        font = TrueTypeFont().true_type_font_from_file(
            Path(path + "/admin_tools/static/fonts/VelaSans-Regular.ttf")
        )
        document = Document()
        page = Page()
        layout = SingleColumnLayout(page)
        layout.add(
            Paragraph(
                f'Toparlaryň "{challenge.name}" ýarysy boýunca netijeleri',
                font=font,
                font_size=Decimal(20),
            )
        )
        if len(results_list) > 10:
            row_count = 11
        else:
            row_count = len(results_list) + 1
        layout.add(
            Paragraph(
                f"Top-10" if row_count == 11 else f"",
                font=font,
                font_size=Decimal(14),
            )
        )
        table = (
            FixedColumnWidthTable(
                number_of_columns=5,
                number_of_rows=row_count,
                column_widths=[
                    Decimal(1),
                    Decimal(1),
                    Decimal(1),
                    Decimal(1),
                    Decimal(1),
                ],
            )
            .add(
                Paragraph(
                    "Ýer",
                    font=font,
                )
            )
            .add(
                Paragraph(
                    "Ady",
                    font=font,
                )
            )
            .add(
                Paragraph(
                    "Familiýasy",
                    font=font,
                )
            )
            .add(
                Paragraph(
                    "Topar",
                    font=font,
                )
            )
            .add(
                Paragraph(
                    "Bal",
                    font=font,
                )
            )
        )
        sh = 0
        for result in results_list:
            if sh == 10:
                break
            sh += 1
            table.add(Paragraph(str(sh), font=font))
            table.add(Paragraph(result["first_name"], font=font))
            table.add(Paragraph(result["last_name"], font=font))
            table.add(Paragraph(result["team"], font=font))
            table.add(Paragraph(str(result["points"]), font=font))

        layout.add(
            table.set_padding_on_all_cells(
                Decimal(3), Decimal(3), Decimal(3), Decimal(3)
            )
        )

        document.add_page(page)

        with open(
            path + f"/media/exported_pdf/{challenge_slug}_users.pdf", "wb"
        ) as pdf_file_handle:
            PDF.dumps(pdf_file_handle, document)

        return render(
            request,
            "personal_result.html",
            {
                "results": results,
                "challenge": challenge,
                "xlsx_path": f"/media/exported_xlsx/{challenge_slug}_users.xlsx",
                "pdf_path": f"/media/exported_pdf/{challenge_slug}_users.pdf",
            },
        )
    else:
        return redirect("home")
