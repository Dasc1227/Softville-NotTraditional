from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from calendar.models import Appointment


def index(request):

    return render(request, "index.html", {
        "index": "Hola",
        "title": "Title"
    })