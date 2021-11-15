from django.shortcuts import render

# Create your views here.
# from appointments.models import Appointment


def index(request):

    return render(request, "index.html", {
        "index": "Hola",
        "title": "Title"
    })
