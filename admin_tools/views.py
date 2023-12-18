import random

import pandas as pd
from django.shortcuts import redirect, render

from main.models import Team, User,

from .forms import XlsxForm
from .models import Xlsxes


class Stub:
    is_superuser = False


def register_tools(request):
    form = XlsxForm()

    try:
        user = User.objects.get(username=request.user.username)
    except:
        user = Stub()
    if user.is_superuser:
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
                    username = (
                        name.lower() + surname.lower() + str(random.randint(1000, 2000))
                    )
                    password = (
                        random.choice([name, surname])
                        + random.choice([name, surname])
                        + str(random.randint(1000, 2000))
                    )

                    user_data["Ady"].append(name)
                    user_data["Familiyasy"].append(surname)
                    user_data["Login"].append(username)
                    user_data["Password"].append(password)
                    user_data["Email"].append(email)
                    user_data["Topar"].append(dataframe["Topar"][i])

                    team = Team.objects.get(name=dataframe["Topar"][i])
                    User.objects.create_user(
                        username=username,
                        password=password,
                        name=name,
                        password_for_usage=password,
                        surname=surname,
                        email=email,
                        team=team,
                    )

                export_path = f"/media/exported_xlsx/{Xlsxes.objects.last().file}"
                dataframe = pd.DataFrame(user_data)
                dataframe.to_excel(f".{export_path}")

                request.session["path"] = export_path

                return redirect("admin_tools")
        if request.session.get("path"):
            download_path = request.session["path"]
            del request.session["path"]

            context = {"form": form, "path": download_path, "download": True}
            return render(request, "admin_tools_page.html", context)
        else:
            context = {"form": form}
            return render(request, "register_tools.html", context)

    else:
        return redirect("home")


# stub
def admin_tools(request):
    return render(request, "admin_tools.html")
