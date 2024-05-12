import datetime
import hashlib
import os
import random
import zipfile
import zoneinfo
from ast import literal_eval
from datetime import date, datetime

import qrcode
import stegano
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

from bookstore.models import CtfTaskObjects, UserDatas
from main.models import File, FlagsFromUnsafety, Team, User

from .forms import ChallengeForm, Hint, QuizzForm
from .models import Answer, Challenge, HashResponse, Hint, Quizz, TrueAnswers
from .tools import *

base_dir = str(settings.BASE_DIR).replace("\\", "/")


@login_required(login_url="login")
def viewChallenge(request):
    challenges = {}
    if request.user.is_superuser or request.user.is_stuff:
        challenges = Challenge.objects.all().filter()
        is_super = "yes"
    else:
        is_super = "no"

    context = {"challenges": challenges, "is_super": is_super}
    return render(request, "challenge.html", context)


@login_required(login_url="login")
def create_challenge(request):
    if request.user.is_superuser:
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
    else:
        return redirect("home")


@login_required(login_url="login")
def create_challenge_quizz(request, pk):
    if request.user.is_superuser:
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

            type_of_quizz = request.POST.get("type-of-quizz")

            files_count = int(request.POST.get("files_count"))

            hints = request.POST.getlist("hint")
            hint_points = request.POST.getlist("hint_point")

            quizz = Quizz.objects.create(
                challenge_id=pk,
                name=_name,
                question=_question,
                point=_point,
                type_of_quizz=type_of_quizz,
            )

            if bookstore_username and bookstore_password:
                CtfTaskObjects.objects.create(
                    username=bookstore_username,
                    password=bookstore_password,
                    for_quizz=quizz.pk,
                )

            if files_count:
                if type_of_quizz != "Steganography":
                    for index in range(1, files_count + 1):
                        File.objects.create(
                            file=request.FILES[f"file{index}"],
                            quizz_id=quizz.pk,
                        )
                else:
                    for index in range(1, files_count + 1):
                        File.objects.create(
                            file=request.FILES[f"file{index}"],
                            quizz_id=quizz.pk,
                            for_team="status:stegano_pub",
                        )

            if _answer and type_of_quizz == "Default":
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
    else:
        return redirect("home")


@login_required(login_url="login")
def display_quizzes(request, pk):
    if request.user.is_superuser:
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

        context = {
            "challenge": challenge,
            "quizzes": quizzes,
            "hintCounts": hint_counts,
        }

        return render(request, "display_quizzes.html", context)
    else:
        return redirect("home")


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


@login_required(login_url="login")
def join_challenge(request, pk):
    if request.user.is_superuser:
        return redirect("home")
    else:
        challenge = Challenge.objects.get(id=pk)

        context = {"challenge": challenge}
        return render(request, "join_challenge.html", context)


@login_required(login_url="login")
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


@login_required(login_url="login")
def play_challenge(request, pk):
    if request.user.is_superuser:
        return redirect("home")
    else:
        challenge = Challenge.objects.get(id=pk)
        if challenge.date_end > datetime.now(
            tz=zoneinfo.ZoneInfo("America/New_York")
        ) and challenge.date_start < datetime.now(
            tz=zoneinfo.ZoneInfo("America/New_York")
        ):
            quizzes = Quizz.objects.filter(challenge_id=pk)

            completed = {}
            status = {}

            score = 0
            timer_timeout_year = f"{challenge.date_end.year}"
            timer_timeout_month = (
                f"{int(challenge.date_end.month) - 1}, {challenge.date_end.day}"
            )
            timer_timeout_hours = f"{int(challenge.date_end.hour) + 5}, {challenge.date_end.minute}, {challenge.date_end.second}, 0"

            for quizz in quizzes:
                answers = Answer.objects.filter(
                    quizz_id=quizz.pk, team=request.user.team.name
                )

                for answer in answers:
                    score += answer.point

                obj_status = (
                    True
                    if Answer.objects.filter(
                        quizz_id=quizz.pk, team=request.user.team.name, status="True"
                    ).exists()
                    else False
                )
                if obj_status == True:
                    status[quizz.pk] = "True"
                else:
                    status[quizz.pk] = "False"

                if (
                    TrueAnswers.objects.filter(
                        quizz_id=quizz.pk, for_team=request.user.team.name
                    ).exists()
                    or TrueAnswers.objects.filter(
                        quizz_id=quizz.pk, for_team=None
                    ).exists()
                ):
                    pass
                else:
                    cycle = random.randint(10, 30)
                    inflag = ""
                    for i in range(cycle):
                        inflag += random.choice(
                            [chr(random.randint(97, 122)), chr(random.randint(65, 90))]
                        )
                        flag = "flag{" + inflag + "}"
                    true_answer = TrueAnswers.objects.create(
                        answer=flag, for_team=request.user.team.name, quizz_id=quizz.pk
                    )
                    if quizz.type_of_quizz == "Pentest":
                        UserDatas.objects.create(
                            flag=flag,
                            for_team=request.user.team.name,
                            quizz_id=quizz.pk,
                        )

                    files_directory = base_dir + "/media/"
                    team = Team.objects.get(name=request.user.team.name)
                    if quizz.type_of_quizz == "Steganography":
                        pict_id = random.randint(1, 1000000)
                        file = File.objects.get(
                            quizz_id=quizz.pk, for_team="status:stegano_pub"
                        )

                        s = stegano.lsb.hide(files_directory + str(file.file), flag)
                        s.save(
                            files_directory
                            + f"files/team{team.name.lower()}{pict_id}.png"
                        )
                        File.objects.create(
                            file=f"files/team{team.name.lower()}{pict_id}.png",
                            quizz_id=quizz.pk,
                            for_team=team.name,
                        )
                    if quizz.type_of_quizz == "Hash":
                        hash_type = (
                            "md5",
                            "sha1",
                            "sha224",
                            "sha256",
                            "sha384",
                            "sha512",
                        )
                        words_tuple = (
                            "query",
                            "wet",
                            "require",
                            "trouble",
                            "gun",
                            "young",
                            "ufo",
                            "include",
                            "opposite",
                            "aproach",
                            "select",
                            "destroy",
                            "fear",
                            "huge",
                            "jade",
                            "key",
                            "liar",
                            "zero",
                            "xor",
                            "crush",
                            "verbose",
                            "box",
                            "nearby",
                            "mix",
                        )
                        link = "127.0.0.1:8000/hash/decode/"
                        words = ""
                        words_range = random.randint(2, 4)
                        for i in range(words_range):
                            word = random.choice(words_tuple)
                            if words_range - 1 == i:
                                words += word
                            else:
                                words += word + "-"

                        link += words

                        hash_response = HashResponse.objects.create(
                            key_words=words,
                            url=link,
                            team=request.user.team.name,
                            flag=flag,
                        )
                        byte_link = literal_eval(f"b'{link}'")
                        current_type = random.choice(hash_type)

                        if current_type == "md5":
                            hash_link = hashlib.md5(byte_link).hexdigest()
                        elif current_type == "sha1":
                            hash_link = hashlib.sha1(byte_link).hexdigest()
                        elif current_type == "sha224":
                            hash_link = hashlib.sha224(byte_link).hexdigest()
                        elif current_type == "sha256":
                            hash_link = hashlib.sha256(byte_link).hexdigest()
                        elif current_type == "sha384":
                            hash_link = hashlib.sha384(byte_link).hexdigest()
                        elif current_type == "sha512":
                            hash_link = hashlib.sha512(byte_link).hexdigest()

                        with open(
                            base_dir + f"/media/txt/{request.user.username}.txt",
                            "w+",
                        ) as file:
                            file.write(hash_link)

                        File.objects.create(
                            file=f"txt/{request.user.username}.txt",
                            for_team=team.name,
                            quizz_id=quizz.pk,
                        )
                        Hint.objects.create(
                            quizz_id=quizz.pk,
                            content=current_type.upper(),
                            point=5,
                            for_team=request.user.team.name,
                        )

                    if quizz.type_of_quizz == "One Time Pad":
                        inflag = ""
                        for i in range(30):
                            inflag += random.choice(
                                [
                                    chr(random.randint(97, 122)),
                                    chr(random.randint(65, 90)),
                                ]
                            )
                        flag = "flag{" + inflag + "}"
                        true_answer.answer = flag
                        true_answer.save()

                        a_cipher, b_cipher = one_time_pad(flag)

                        txt_id = random.randint(10000, 1000000)
                        with open(
                            base_dir
                            + f"/media/one/{request.user.username}{txt_id}.txt",
                            "w+",
                        ) as file:
                            file.write("A: " + a_cipher + "\n")
                            file.write("B: " + b_cipher + "\n")

                        File.objects.create(
                            file=f"one/{request.user.username}{txt_id}.txt",
                            quizz_id=quizz.pk,
                            for_team=request.user.team.name,
                        )

                    if quizz.type_of_quizz == "RSA":
                        dir_id = random.randint(10000, 1000000)
                        dir_path = (
                            files_directory + f"sa/{request.user.username}{dir_id}"
                        )
                        media_path = f"sa/{request.user.username}{dir_id}/"
                        os.mkdir(dir_path)
                        rsa_encrypt(flag, dir_path)

                        File.objects.create(
                            file=f"{media_path}i_am.pem",
                            quizz_id=quizz.pk,
                            for_team=request.user.team.name,
                        )
                        File.objects.create(
                            file=f"{media_path}decrypt_me.message",
                            quizz_id=quizz.pk,
                            for_team=request.user.team.name,
                        )

                    if quizz.type_of_quizz == "AES":
                        dir_id = random.randint(10000, 1000000)
                        dir_path = (
                            files_directory + f"ae/{request.user.username}{dir_id}"
                        )
                        media_path = f"ae/{request.user.username}{dir_id}/"
                        os.mkdir(dir_path)
                        aes_encrypt(flag, dir_path)

                        File.objects.create(
                            file=f"{media_path}pointless.txt",
                            quizz_id=quizz.pk,
                            for_team=request.user.team.name,
                        )
                        File.objects.create(
                            file=f"{media_path}cipher.bin",
                            quizz_id=quizz.pk,
                            for_team=request.user.team.name,
                        )
                        File.objects.create(
                            file=f"{media_path}salt",
                            quizz_id=quizz.pk,
                            for_team=request.user.team.name,
                        )

                    if quizz.type_of_quizz == "QR":
                        pict_id = random.randint(1, 1000000)

                        fake_id = random.randint(1, 99)
                        qr_code = qrcode.make(
                            f"http://127.0.0.1:8000/challenge/quizz/{fake_id}"
                        )
                        qr_code_path = (
                            files_directory
                            + f"def_qrs/{request.user.username}{pict_id}.png"
                        )
                        qr_code.save(qr_code_path)

                        s = stegano.lsb.hide(qr_code_path, flag)
                        s.save(
                            files_directory + f"ol/team{team.name.lower()}{pict_id}.png"
                        )
                        File.objects.create(
                            file=f"ol/team{team.name.lower()}{pict_id}.png",
                            quizz_id=quizz.pk,
                            for_team=team.name,
                        )

                    if quizz.type_of_quizz == "Transposition":
                        txt_id = random.randint(10000, 1000000)
                        cipher = transposition_cipher(flag)
                        with open(
                            base_dir + f"/media/tr/{request.user.username}{txt_id}.txt",
                            "w+",
                        ) as file:
                            file.write(cipher)

                        File.objects.create(
                            file=f"tr/{request.user.username}{txt_id}.txt",
                            quizz_id=quizz.pk,
                            for_team=request.user.team.name,
                        )

                    if quizz.type_of_quizz == "Format Game":
                        picture_path = (
                            base_dir
                            + "/main/static/challenge_files/format_challenge.png"
                        )
                        media_path = f"for/{request.user.username}{random.randint(10000, 1000000)}"
                        new_picture_path = base_dir + f"/media/" + media_path
                        image = Image.open(picture_path)
                        font = ImageFont.truetype("arial.ttf", 48)
                        drawer = ImageDraw.Draw(image)
                        drawer.text((50, 100), flag)

                        image.save(new_picture_path + ".png")

                        os.rename(new_picture_path + ".png", new_picture_path + ".txt")

                        File.objects.create(
                            file=media_path + ".txt",
                            quizz_id=quizz.pk,
                            for_team=request.user.team.name,
                        )

                    if quizz.type_of_quizz == "Caesar":
                        cycle = random.randint(10, 30)
                        inflag = ""
                        for i in range(cycle):
                            inflag += chr(random.randint(97, 122))
                            flag = "flag{" + inflag + "}"
                        true_answer.answer = flag
                        true_answer.save()

                        offset = random.randint(3, 9)
                        keys, invKeys = generate_caesar_cypher(offset)
                        encrypted = encrypt_caesar(inflag, keys)

                        txt_id = random.randint(10000, 1000000)
                        with open(
                            base_dir + f"/media/ca/{request.user.username}{txt_id}.txt",
                            "w+",
                        ) as file:
                            file.write(encrypted)

                        File.objects.create(
                            file=f"ca/{request.user.username}{txt_id}.txt",
                            quizz_id=quizz.pk,
                            for_team=request.user.team.name,
                        )

                    if quizz.type_of_quizz == "Affine":

                        txt_id = random.randint(10000, 1000000)
                        cipher = affine(flag)
                        with open(
                            base_dir + f"/media/af/{request.user.username}{txt_id}.txt",
                            "w+",
                        ) as file:
                            file.write(cipher)

                        File.objects.create(
                            file=f"af/{request.user.username}{txt_id}.txt",
                            quizz_id=quizz.pk,
                            for_team=request.user.team.name,
                        )

                    if quizz.type_of_quizz == "Vigenere":
                        cycle = random.randint(10, 30)
                        inflag = ""
                        for i in range(cycle):
                            inflag += chr(random.randint(97, 122))
                        inflag = inflag.lower()
                        flag = "flag{" + inflag + "}"
                        true_answer.answer = flag
                        true_answer.save()

                        dir_id = random.randint(10000, 1000000)
                        dir_path = (
                            files_directory + f"vi/{request.user.username}{dir_id}"
                        )
                        media_path = f"vi/{request.user.username}{dir_id}/"
                        os.mkdir(dir_path)
                        vigenere_encrypt(inflag, dir_path)

                        File.objects.create(
                            file=f"{media_path}cipher.txt",
                            quizz_id=quizz.pk,
                            for_team=request.user.team.name,
                        )

                    if quizz.type_of_quizz == "Morse":
                        cycle = random.randint(10, 30)
                        inflag = ""
                        for i in range(cycle):
                            inflag += chr(random.randint(97, 122))
                        inflag = inflag.lower()
                        flag = "flag{" + inflag + "}"
                        true_answer.answer = flag
                        true_answer.save()

                        file_id = random.randint(10000, 1000000)

                        morse_run(
                            inflag,
                            base_dir
                            + f"/media/mor/{request.user.username}{file_id}.mp3",
                        )

                        File.objects.create(
                            file=f"mor/{request.user.username}{file_id}.mp3",
                            quizz_id=quizz.pk,
                            for_team=request.user.team.name,
                        )

                    if quizz.type_of_quizz == "Enigma":
                        cycle = random.randint(10, 30)
                        inflag = ""
                        for i in range(cycle):
                            inflag += chr(random.randint(97, 122))
                        flag = "flag{" + inflag + "}"
                        true_answer.answer = flag
                        true_answer.save()

                        enigma = Encryptor().encrypt(inflag)

                        txt_id = random.randint(10000, 1000000)
                        with open(
                            base_dir + f"/media/en/{request.user.username}{txt_id}.txt",
                            "w+",
                        ) as file:
                            file.write(enigma)

                        File.objects.create(
                            file=f"en/{request.user.username}{txt_id}.txt",
                            quizz_id=quizz.pk,
                            for_team=request.user.team.name,
                        )

                    if quizz.type_of_quizz == "Matreshka":
                        txt_id = random.randint(1, 1000000)
                        lines_count = random.randint(75, 500)
                        flag_line = random.randint(75, lines_count)
                        text = ""
                        for line_id in range(lines_count):
                            text += (
                                "".join(
                                    [
                                        chr(random.randint(97, 122))
                                        for i in range(random.randint(50, 150))
                                    ]
                                )
                                + "\n"
                            )
                            if line_id == flag_line:
                                text += flag + "\n"
                        path = (
                            files_directory
                            + f"files/team{''.join(team.name.lower().split())}{txt_id}"
                        )
                        os.mkdir(path)
                        cwd = os.getcwd()
                        os.chdir(
                            f"media/files/team{''.join(team.name.lower().split())}{txt_id}"
                        )
                        with open("data.txt", "w+") as file:
                            file.write(text)
                        os.rename("data.txt", "data")

                        with zipfile.ZipFile("data_archive.zip", "w") as zipFile:
                            zipFile.write("data")
                        os.remove("data")
                        os.rename("data_archive.zip", "data")
                        nested_zip = random.randint(3, 10)
                        for i in range(nested_zip):
                            with zipfile.ZipFile("data_archive.zip", "w") as zipFile:
                                zipFile.write("data")
                            os.remove("data")
                            os.rename("data_archive.zip", "data")
                        os.chdir(cwd)
                        File.objects.create(
                            file=f"files/team{''.join(team.name.lower().split())}{txt_id}/data",
                            for_team=team.name,
                            quizz_id=quizz.pk,
                        )

            context = {
                "challenge": challenge,
                "quizzes": quizzes,
                "score": score,
                "status": status,
                "timer_timeout_year": timer_timeout_year,
                "timer_timeout_month": timer_timeout_month,
                "timer_timeout_hours": timer_timeout_hours,
            }
            return render(request, "play_challenge.html", context)
        else:
            return redirect("running")


@login_required(login_url="login")
def play_challenge_quizz(request, pk, pk1):
    if request.user.is_superuser:
        return redirect("home")
    else:
        challenge = Challenge.objects.get(id=pk)
        team = request.user.team.name
        if challenge.date_end > datetime.now(
            tz=zoneinfo.ZoneInfo("Asia/Ashgabat")
        ) and challenge.date_start < datetime.now(
            tz=zoneinfo.ZoneInfo("Asia/Tashkent")
        ):
            quizz = Quizz.objects.get(id=pk1)

            timer_timeout_year = f"{challenge.date_end.year}"
            timer_timeout_month = (
                f"{int(challenge.date_end.month) - 1}, {challenge.date_end.day}"
            )
            timer_timeout_hours = f"{int(challenge.date_end.hour) + 5}, {challenge.date_end.minute}, {challenge.date_end.second}, 0"
            hints = Hint.objects.filter(
                quizz_id=quizz.id, for_team=request.user.team.name
            ) | Hint.objects.filter(quizz_id=quizz.id, for_team="status:public")
            files = File.objects.filter(
                quizz_id=pk1, for_team=request.user.team.name
            ) | File.objects.filter(quizz_id=pk1, for_team="status:public")

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
            context = {
                "challenge": challenge,
                "quizz": quizz,
                "hints": hints,
                "files": files,
                "timer_timeout_year": timer_timeout_year,
                "timer_timeout_month": timer_timeout_month,
                "timer_timeout_hours": timer_timeout_hours,
            }

            unsafety_flags = [flag.flag for flag in FlagsFromUnsafety.objects.all()]

            if request.method == "POST":
                _answer = request.POST.get("answer")
                minus_point = request.POST.get("minus-point")
                # print('begin')
                # print(minus_point)

                if (
                    _answer == true_answer.answer
                    and quizz.type_of_quizz != "SQL Injection"
                ):
                    _point = quizz.point - int(minus_point)
                    _status = "True"
                elif (
                    quizz.type_of_quizz == "SQL Injection" and _answer in unsafety_flags
                ):
                    _point = quizz.point - int(minus_point)
                    _status = "True"
                else:
                    _point = 0
                    _status = "False"

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
        else:
            return redirect("running")

    return render(request, "play_challenge_quizz.html", context)


def fake_quizz(request, quizz_id):
    return render(request, "fake_quizz.html")
