from django.shortcuts import render
from django.http import HttpResponse
import json
import os
from django.shortcuts import render, redirect
from .forms import AktivitaetForm
from django.core.files.storage import FileSystemStorage
import datetime



def time_ago(dt):
  now = datetime.datetime.now()
  diff = now - dt

  seconds = diff.total_seconds()

  if seconds < 60:
    return "gerade eben"
  elif seconds < 3600:
    return f"vor {int(seconds // 60)} Minuten"
  elif seconds < 86400:
    return f"vor {int(seconds // 3600)} Stunden"
  else:
    return f"vor {int(seconds //86400)} Tagen"


def activity_form(request):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    DATA_FILE = os.path.join(current_dir, "data.json")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        category = request.POST.get("category")
        date = datetime.datetime.now().isoformat()

        image = request.FILES.get("image")
        image_name = None
        file_url = None

        if image:
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            file_url = fs.url(filename)
            image_name = filename

        new_entry = {
            "title": title,
            "description": description,
            "category": category,
            "image": image_name,
            "image_url": file_url,
            "date": date,
            "participant": [],
        }

        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []

        data.append(new_entry)

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


        return HttpResponse("Stark")

    return render(request, "friendsly/activity-formular.html")



def ausgabe(request):
  current_dir = os.path.dirname(os.path.abspath(__file__))
  DATA_FILE = os.path.join(current_dir, "data.json")

  if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
      data = json.load(f)

    for entry in data:
      if "date" in entry:
        dt = datetime.datetime.fromisoformat(entry["date"])
        entry["time_ago"] = time_ago(dt)
  else:
    data = []

  return render(request, "friendsly/auflistung.html", {"entries": data})


def login(request):
  # Pfad zum aktuellen Verzeichnis der views.py
  current_dir = os.path.dirname(os.path.abspath(__file__))

  # Pfad zur JSON-Datei
  password_file = os.path.join(current_dir, "passwords.json")

  # Datei öffnen und laden
  with open(password_file, "r") as f:
    passwords = json.load(f)

  if request.method == "POST":
    user = request.POST["user"]
    password = request.POST["password"]

    if user in passwords and passwords[user] == password:
      response = redirect("abo")
      response.set_cookie("login", "True")
      response.set_cookie("user", user)
      return response
    else:
      return render(request, "friendsly/login_page.html")
  else:
    return render(request, "friendsly/login_page.html")

def abo(request):
  if request.COOKIES.get("login") == "True":
    return render(request, "friendsly/abo.html")
  else:
    return redirect("login")

def explore(request):
  return render(request, "friendsly/Explorepage.html")

def profil(request):
  if "user" in request.COOKIES:
    user = request.COOKIES["user"]
    return render(request, "friendsly/profil.html", {"user":user})
  else:
    return render(request, "friendsly/profil.html", {"user":"Fehler"})

def registrierung(request):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    password_file = os.path.join(current_dir, "passwords.json")

    with open(password_file, "r") as f:
        passwords = json.load(f)

    if request.method == "POST":
        user = request.POST["user"]
        password = request.POST["password"]
        password2 = request.POST["password2"]

        if password == password2:
            if user not in passwords:
                passwords[user] = password

                
                with open(password_file, "w") as f:
                    json.dump(passwords, f, indent=4)

                return redirect("login")  # oder direkt einloggen

            else:
                return render(request, "friendsly/create_account.html", {
                    "error": "User existiert bereits"
                })

        else:
            return render(request, "friendsly/create_account.html", {
                "error": "Passwörter stimmen nicht überein"
            })

    return render(request, "friendsly/create_account.html")
# Create your views here.

