from django.urls import reverse

from appointments.models import Appointment, Worker, Patient
from datetime import date, timedelta

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

        # TODO: Delete warning by adding time zone in this appointments
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

    def test_appointment_exist(self, setup, logged_user):
        client, user = logged_user()
        path = reverse("list_appointments")
        response = client.get(path)
        appointments_list = response.context["appointments_week"]
        assert len(appointments_list[0]["appointments"]) > 0

    # TODO: Skipping since this test file is pending to review by its owner
    @pytest.mark.skip
    def test_appointment_do_not_exist(self, setup, logged_user):
        client, user = logged_user()
        path = reverse("list_appointments")
        response = client.get(path)
        appointments_list = response.context["appointments_week"]
        assert len(appointments_list[1]["appointments"]) > 0

    def test_appointment_other_day_of_week(self, setup, logged_user):
        client, user = logged_user()
        path = reverse("list_appointments")
        response = client.get(path)
        appointments_list = response.context["appointments_week"]
        assert len(appointments_list[2]["appointments"]) > 0
