from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from datetime import timedelta

from appointments.forms import Register_appointment_form

from appointments.models import Appointment, Worker, Patient
from datetime import date
from datetime import datetime


@login_required(login_url='/login')
def index(request):
    return render(request, "index.html")


def login_view(request):
    context = {}
    if request.method == "POST":
        # Attempt to sign user in
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)

        # Check if authentication is successful
        if user is not None:
            user.password_attempts = 0
            user.save()
            login(request, user)
            if request.POST.get("next"):
                return HttpResponseRedirect(request.POST.get("next"))
            else:
                return HttpResponseRedirect(reverse("index"))
        else:
            user = Worker.objects.get(email=email)
            # User exists, but could not be authenticated (incorrect password)
            if user is not None:
                context["error"] = "Contraseña inválida."
                user.password_attempts += 1

                # Check if user is blocked
                if user.password_attempts >= 5:
                    user.is_active = False

                user.save()

                context["user_blocked"] = user.is_active
                context["login_attempts"] = 5 - user.password_attempts
            else:
                context["error"] = "El correo no existe en el sistema."

            return render(request, "login.html", context)
    elif request.user.is_anonymous:
        return render(request, "login.html")
    else:
        return HttpResponseRedirect(reverse("index"))


@login_required(login_url='/login')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


@login_required(login_url='/login')
def register_appointment(request):
    context = {'workers': Worker.objects.all()}
    if request.method == "POST":
        form = Register_appointment_form(request.POST)
        if form.is_valid():
            date = form.cleaned_data["inputDate"]
            time = form.cleaned_data["inputTime"]
            worker_choice = form.cleaned_data["workerSelected"]
            worker = Worker.objects.get(email=worker_choice)
            patient_name = form.cleaned_data["inputName"]
            patient_LastName = form.cleaned_data["inputLastName"]
            patient_id = form.cleaned_data["inputPatientID"]
            patient_email = form.cleaned_data["inputEmail"]
            register = request.user
            patient, created = Patient.objects.get_or_create(
                id_number=patient_id,
                name=patient_name,
                last_name=patient_LastName,
                email=patient_email,
            )
            dateTime = datetime.combine(date, time)
            ap = Appointment(registered_by=register, attended_by=worker,
                             patient_id=patient, start_time=dateTime)
            ap.save()

        else:
            context["form"] = form

    return render(request, "register_appointment.html", context)


@login_required(login_url='/login')
def list_appointments(request):
    start_date = date.today()

    # Appointments for the next 7 days
    appointments_week = [
        {
            "day": (start_date + timedelta(days=day)),
            "appointments": Appointment.objects.filter(
                start_time__date=(start_date + timedelta(days=day))
            ).order_by('start_time')
        }
        for day in range(0, 7)
    ]

    return render(request, "list_appointments.html", {
        "appointments_week": appointments_week,
    })
