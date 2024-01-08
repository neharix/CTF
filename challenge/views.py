import datetime
import random

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from bookstore.models import ConnectionJournal, CtfTaskObjects, UserDatas
from main.models import File, Team, User

from .forms import ChallengeForm, Hint, QuizzForm
from .models import Answer, Challenge, Hint, Quizz, TrueAnswers


@login_required(login_url="login")
def viewChallenge(request):
    challenges = {}
    if request.user.is_superuser:
        challenges = Challenge.objects.all().filter(owner=request.user)
        is_super = "yes"
    else:
        is_super = "no"

    print(is_super)

    context = {"challenges": challenges, "is_super": is_super}
    return render(request, "challenge.html", context)


@login_required(login_url="login")
def create_challenge(request):
    form = ChallengeForm()
    if request.method == "POST":
        form = ChallengeForm(request.POST)
        if form.is_valid():
            name = request.POST.get("name")
            date_start = request.POST.get("date_start")
            date_end = request.POST.get("date_end")
            description = request.POST.get("description")
            public = (
                request.POST.get("public")
                if request.POST.get("public") != None
                else False
            )

            challenge = Challenge.objects.create(
                name=name,
                owner=str(request.user),
                date_start=date_start,
                date_end=date_end,
                description=description,
                public=public,
            )
            challenge.save()
            # print(form)
            return redirect(create_challenge_quizz, pk=challenge.id)
            # return redirect(f'create_challenge_quizz/{challenge.id}/')

    context = {"form": form}
    return render(request, "create_challenge.html", context)


@login_required(login_url="login")
def create_challenge_quizz(request, pk):
    challenge = Challenge.objects.get(id=pk)
    name = challenge.name
    context = {"name": name}

    if request.method == "POST":
        _name = request.POST.get("name")
        _question = request.POST.get("question")
        _answer = request.POST.get("answer")
        _point = request.POST.get("point")

        bookstore_username = request.POST.get("ctf_username")
        bookstore_password = request.POST.get("ctf_password")

        files_count = int(request.POST.get("files_count"))

        if bookstore_username and bookstore_password:
            CtfTaskObjects.objects.create(
                username=bookstore_username, password=bookstore_password
            )
            is_pentest = True
        else:
            is_pentest = False

        hints = request.POST.getlist("hint")
        hint_points = request.POST.getlist("hint_point")

        quizz = Quizz.objects.create(
            challenge_id=pk,
            name=_name,
            question=_question,
            point=_point,
            is_pentest=is_pentest,
        )

        if files_count:
            for index in range(1, files_count + 1):
                File.objects.create(
                    file=request.FILES[f"file{index}"], quizz_id=quizz.pk
                )

        if _answer:
            TrueAnswers.objects.create(
                is_public=True, answer=_answer, quizz_id=quizz.pk
            )
        quizz.save()

        for content, hint_point in zip(hints, hint_points):
            hint = Hint.objects.create(
                quizz_id=quizz.id, content=content, point=hint_point
            )
            hint.save()

    context = {"challenge": challenge}
    return render(request, "create_challenge_quizz.html", context)


@login_required(login_url="login")
def display_quizzes(request, pk):
    challenge = Challenge.objects.get(id=pk)
    quizzes = (
        Quizz.objects.all()
        .filter(challenge_id=pk)
        .values("id", "name", "question", "point")
    )

    hint_counts = []

    if request.method == "POST" and "Delete" in request.POST:
        print("yes")
        quizzes = Quizz.objects.filter(challenge_id=pk)
        for quizz in quizzes:
            id = quizz.id
            Hint.objects.filter(quizz_id=id).delete()
        quizzes.delete()
        challenge.delete()
        return redirect(viewChallenge)

    if request.method == "POST":
        print(request.POST)

    if request.method == "POST" and "changePrivate" in request.POST:
        print("yes")
        Challenge.objects.filter(id=pk).update(public="False")
        return redirect(display_quizzes, pk)

    if request.method == "POST" and "changePublic" in request.POST:
        print("yes")
        Challenge.objects.filter(id=pk).update(public="True")
        return redirect(display_quizzes, pk)

    for quizz in quizzes:
        id = quizz["id"]
        hint_count = Hint.objects.all().filter(quizz_id=id).count()
        hint_counts.append(hint_count)

    context = {"challenge": challenge, "quizzes": quizzes, "hintCounts": hint_counts}

    return render(request, "display_quizzes.html", context)


@login_required(login_url="login")
def edit_quizz(request, pk, pk1):
    quizz = Quizz.objects.get(id=pk1)

    form = QuizzForm()

    hints = Hint.objects.filter(quizz_id=pk1).values("content", "point")

    files = File.objects.filter(quizz_id=pk1)

    if request.method == "POST":
        if "Submit" in request.POST:
            form = QuizzForm(request.POST, request.FILES, instance=quizz)
            # print(form)
            if form.is_valid():
                Hint.objects.filter(quizz_id=pk1).delete()
                hints = request.POST.getlist("hint")
                hint_points = request.POST.getlist("hint_point")
                # print(hints)

                for content, hint_point in zip(hints, hint_points):
                    hint = Hint.objects.create(
                        quizz_id=pk1, content=content, point=hint_point
                    )
                    hint.save()

                form.save()
        else:
            quizz.delete()
        return redirect(display_quizzes, pk=pk)

        # form=QuizzForm(request.POST)
        # hintss = request.POST.getlist('hint')
        # hint_points = request.POST.getlist('hint_point')
        # print(hintss)

    context = {
        "form": form,
        "quizz": quizz,
        "challenge_id": pk,
        "hints": hints,
        "files": files,
    }
    return render(request, "edit_a_quizz.html", context)


def join_challenge(request, pk):
    challenge = Challenge.objects.get(id=pk)

    context = {"challenge": challenge}
    return render(request, "join_challenge.html", context)


def register_challenge(request, pk):
    challenge = Challenge.objects.get(id=pk)

    creator = User.objects.get(username=challenge.owner)
    creator_name = creator.name

    try:
        registered = "yes"
    except:
        registered = "no"

    if request.method == "POST":
        _content = challenge.name + " has started. Join us now!"

        return redirect("upcoming")

    # print(creator_name)
    context = {
        "challenge": challenge,
        "creator_name": creator_name,
        "registered": registered,
    }
    return render(request, "register_challenge.html", context)


def expired_challenge(request, pk):
    challenge = Challenge.objects.get(id=pk)

    creator = User.objects.get(username=challenge.owner)
    creator_name = creator.name

    context = {"challenge": challenge, "creator_name": creator_name}
    return render(request, "expired_challenge.html", context)


def play_challenge(request, pk):
    challenge = Challenge.objects.get(id=pk)

    if challenge.date_end > datetime.now() and challenge.date_start < datetime.now():
        quizzes = Quizz.objects.filter(challenge_id=pk)

        completed = {}
        status = {}

        score = 0

        for quizz in quizzes:
            try:
                obj = Answer.objects.get(
                    quizz_id=quizz.pk, username=request.user.username
                )
                completed[quizz.pk] = "yes"
                if obj.status == "True":
                    status[quizz.pk] = "True"
                else:
                    status[quizz.pk] = "False"
                score += obj.point
            except Answer.DoesNotExist:
                completed[quizz.pk] = "no"
                pass

            if (
                quizz.is_pentest
                and len(
                    TrueAnswers.objects.filter(
                        quizz_id=quizz.pk, for_team=request.user.team.name
                    )
                )
                == 0
            ):
                cycle = random.randint(10, 30)
                inflag = ""
                for i in range(cycle):
                    inflag += random.choice(
                        [chr(random.randint(97, 122)), chr(random.randint(65, 90))]
                    )
                flag = "flag{" + inflag + "}"

                UserDatas.objects.create(flag=flag, for_team=request.user.team.name)
                TrueAnswers.objects.create(
                    answer=flag, for_team=request.user.team.name, quizz_id=quizz.pk
                )

        context = {
            "challenge": challenge,
            "quizzes": quizzes,
            "completed": completed,
            "score": score,
            "status": status,
        }
        return render(request, "play_challenge.html", context)
    elif challenge.date_end < datetime.now():
        return redirect("expired")
    elif challenge.date_start > datetime.now():
        return redirect("upcoming")


from datetime import date, datetime

from django.utils import timezone


def play_challenge_quizz(request, pk, pk1):
    challenge = Challenge.objects.get(id=pk)
    team = request.user.team.name
    if challenge.date_end > datetime.now() and challenge.date_start < datetime.now():
        quizz = Quizz.objects.get(id=pk1)
        hints = Hint.objects.filter(quizz_id=quizz.id)

        try:
            true_answer = TrueAnswers.objects.get(
                quizz_id=quizz.pk, for_team=request.user.team.name
            )
        except:
            true_answer = TrueAnswers.objects.get(quizz_id=quizz.pk, is_public=True)

        _point = 0
        _status = "False"
        now = timezone.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        if request.method == "POST":
            _answer = request.POST.get("answer")
            minus_point = request.POST.get("minus-point")
            # print('begin')
            # print(minus_point)
            if _answer == true_answer.answer:
                _point = quizz.point - int(minus_point)
                _status = "True"
            else:
                _point = 0
                _status = "False"

            try:
                obj = Answer.objects.get(quizz_id=quizz.id, team=request.user.team.name)
                _point = int(75 * int(_point) / 100)
                obj.point = _point
                obj.status = _status
                obj.save()
            except Answer.DoesNotExist:
                answer_obj = Answer.objects.create(
                    challenge_id=challenge.id,
                    username=request.user.username,
                    team=team,
                    quizz_id=quizz.id,
                    answer=_answer,
                    point=_point,
                    status=_status,
                )
                answer_obj.save()

            return redirect(play_challenge, pk=pk)
    elif challenge.date_end < datetime.now():
        return redirect("expired")
    elif challenge.date_start > datetime.now():
        return redirect("upcoming")

    # print(hints)

    context = {"challenge": challenge, "quizz": quizz, "hints": hints}
    return render(request, "play_challenge_quizz.html", context)
