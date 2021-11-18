from django.test import RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User

from appointments.views import list_appointments

from appointments.models import Appointment, Worker, Patient
from datetime import date, timedelta
from mixer.backend.django import mixer

import pytest


@pytest.mark.django_db
class TestListAppointments:

    @pytest.fixture
    def setup(self):
        worker_1 = Worker.objects.create(email="as@test.com", id_number="1234",
                                         id_type="PH", first_name="Steven",
                                         last_name="Herrera", is_staff=True,
                                         is_active=True)
        patient_1 = Patient.objects.create(id_number="11899483", name="Samuel",
                                           last_name="Poleski",
                                           email="patient@test.com")
        Appointment.objects.create(registered_by=worker_1,
                                   attended_by=worker_1,
                                   patient_id=patient_1,
                                   start_time=date.today())
        Appointment.objects.create(registered_by=worker_1,
                                   attended_by=worker_1,
                                   patient_id=patient_1,
                                   start_time=(date.today()
                                               + timedelta(days=20)))
        Appointment.objects.create(registered_by=worker_1,
                                   attended_by=worker_1,
                                   patient_id=patient_1,
                                   start_time=date.today() + timedelta(days=2))

    def test_appointment_exist(self, setup):
        path = reverse("list_appointments")
        request = RequestFactory().get(path)
        request.user = mixer.blend(User)
        response = list_appointments(request)
        appointments_list = response.context["appointments_week"]
        assert len(appointments_list[0]["appointments"]) > 0

    def test_appointment_do_not_exist(self, setup):
        path = reverse("list_appointments")
        request = RequestFactory().get(path)
        request.user = mixer.blend(User)
        response = list_appointments(request)
        appointments_list = response.context["appointments_week"]
        assert len(appointments_list[1]["appointments"]) > 0

    def test_appointment_other_day_of_week(self, setup):
        path = reverse("list_appointments")
        request = RequestFactory().get(path)
        request.user = mixer.blend(User)
        response = list_appointments(request)
        appointments_list = response.context["appointments_week"]
        assert len(appointments_list[2]["appointments"]) > 0
