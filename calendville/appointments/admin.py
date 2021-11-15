from django.contrib import admin
from appointments.models import Appointment
from appointments.models import Worker
from appointments.models import Patient

admin.site.register(Appointment)
admin.site.register(Worker)
admin.site.register(Patient)
