from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Appointment(models.Model):
    secretary = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="secretaries")
    patient = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="patients")
    start_time = models.DateTimeField()
