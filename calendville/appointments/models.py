from django.db import models
from django.db.models.deletion import CASCADE


# See the following link for id lengths and types:
# https://help.hulipractice.com/es/articles/1348413-ingresar-informacion-de-emisores-solo-para-costa-rica

class Patient(models.Model):
    id_number = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True)


class Worker(models.Model):
    PHYSICAL = "PH"
    JURIDICAL = "JU"
    NITE = "NI"
    DIMEX = "DM"
    ID_TYPES = [
        (PHYSICAL, 'Física'),
        (JURIDICAL, 'Jurídica'),
        (NITE, 'Número de Identificación Tributario Especial'),
        (DIMEX, 'Documento de Identifcación de Migración y Extrangería')
    ]
    id_number = models.CharField(primary_key=True, max_length=12)
    id_type = models.CharField(max_length=2, choices=ID_TYPES,
                               default=PHYSICAL)
    name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=100, null=False)
    email = models.EmailField(max_length=254, unique=True, null=False)
    # Adding password size as a placeholder, see
    # https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#password-hashing-algorithms
    password = models.CharField(max_length=32, null=False)
    password_attempts = models.PositiveSmallIntegerField(default=0, null=False)

    @classmethod
    def get_sentinel_worker(cls):
        worker, created = cls.objects.get_or_create(
            id_number="0000000000",
            name="deleted",
            last_name="deleted",
            email="",
            password=""
        )
        return worker.id_number


class Appointment(models.Model):
    id = models.AutoField(primary_key=True)
    registered_by = models.ForeignKey(to=Worker, on_delete=models.CASCADE,
                                      related_name="secretary")
    attended_by = models.ForeignKey(to=Worker, on_delete=models.CASCADE,
                                    related_name="health_professional")
    patient_id = models.ForeignKey(to=Patient, on_delete=CASCADE,
                                   related_name="patient")
    start_time = models.DateTimeField()
