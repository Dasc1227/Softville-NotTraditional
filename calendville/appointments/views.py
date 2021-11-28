from datetime import datetime
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from datetime import timedelta

from appointments.models import Appointment, Worker
from datetime import date

from appointments.forms import RegisterAppointmentForm


EMAIL_KEY = "email"
PASSWORD_KEY = "password"


@login_required(login_url='/login')
def index(request):
    return render(request, "index.html")


def login_view(request):
    context = {}
    if request.method == "POST":

        if not (EMAIL_KEY in request.POST and
                PASSWORD_KEY in request.POST):
            context["error"] = "Datos inválidos"
            return render(request, "login.html", context)

        email = request.POST["email"]
        password = request.POST["password"]

        user_entry = Worker.objects.filter(email=email)

        # User exists
        if user_entry.exists():
            # Attempt to sign user in
            user = authenticate(request, username=email, password=password)
            if user is not None:
                user.password_attempts = 0
                user.save()
                login(request, user)
                next_url = request.POST.get("next")
                if next_url:
                    return HttpResponseRedirect(next_url)
                else:
                    return HttpResponseRedirect(reverse("index"))
            else:
                user = user_entry[0]
                context["error"] = "Contraseña inválida."
                user.password_attempts += 1

                # Check if user is blocked
                if user.password_attempts >= 5:
                    user.is_active = False

                user.save()

                context["user_blocked"] = user.is_active
                context["login_attempts"] = 5 - user.password_attempts
        else:
            context["error"] = "El correo no existe en el sistema"

        return render(request, "login.html", context)
    elif request.user.is_anonymous:
        return render(request, "login.html")
    else:
        # GET and user is logged in
        return HttpResponseRedirect(reverse("index"))


@login_required(login_url='/login')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


@login_required(login_url='/login')
def register_appointment(request):
    if request.method == "POST":
        form = RegisterAppointmentForm(request.POST)
        if form.is_valid():
            appointment_date = form.cleaned_data['date']
            appointment_time = form.cleaned_data['time']
            doctor = form.cleaned_data['attended_by']
            patient = form.cleaned_data["patient_id"]
            secretary = request.user
            appointment = Appointment(
                registered_by=secretary,
                attended_by=doctor,
                patient_id=patient,
                start_time=datetime.combine(appointment_date,
                                            appointment_time)
            )
            appointment.save()
    else:
        form = RegisterAppointmentForm()

    return render(request, "register_appointment.html", {
        'form': form
    })


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
