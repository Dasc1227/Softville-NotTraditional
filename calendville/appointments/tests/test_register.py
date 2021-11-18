from datetime import datetime, timedelta, date

from django.test import Client

import pytest
from mixer.backend.django import mixer

from appointments.models import Worker, Patient


@pytest.mark.django_db
class TestRegister:
    HTTP_REDIRECT_CODE = 302
    HTTP_OK_CODE = 200
    REGISTER_URL = "/register_appointment"

    USERNAME_FIELD = "email"
    PASSWORD_FIELD = "password"

    USER = {
        USERNAME_FIELD: "good@mail.com",
        PASSWORD_FIELD: "good_pass"
    }

    @pytest.fixture
    def log_in(self):
        self.client = Client()
        self.user = mixer.blend(Worker)
        self.client.login(username=self.user.email, password=self.user.password)

    @pytest.fixture
    def create_worker(self):
        self.patient = mixer.blend(Patient)
        self.worker = mixer.blend(Worker)

    def test_valid_appointment(self, log_in, create_worker):
        VALID_APPOINTMENT = {
            "inputDate": (date.today() + timedelta(days=1)).strftime("%x"),
            "inputTime": datetime.now().strftime("%X"),
            "inputLastName": self.patient.last_name,
            "inputName": self.patient.name,
            "inputEmail": self.patient.email,
            "inputPatientID": self.patient.id_number,
            "workerSelected": self.worker.email,
        }

        response = self.client.post('/register_appointment', VALID_APPOINTMENT, follow=True)

    def test_past_date_appointment(self, log_in, create_worker):
        PAST_DATE_APPOINTMENT = {
            "inputDate": (date.today() - timedelta(days=1)).strftime("%x"),
            "inputTime": datetime.now().strftime("%X"),
            "inputLastName": self.patient.last_name,
            "inputName": self.patient.name,
            "inputEmail": self.patient.email,
            "inputPatientID": self.patient.id_number,
            "workerSelected": self.worker.email,
        }

        response = self.client.post('/register_appointment', PAST_DATE_APPOINTMENT, follow=True)

    def test_past_time_appointment(self, log_in, create_worker):
        PAST_TIME_APPOINTMENT = {
            "inputDate": date.today().strftime("%x"),
            "inputTime": (datetime.now() - timedelta(hours=1)).strftime("%X"),
            "inputLastName": self.patient.last_name,
            "inputName": self.patient.name,
            "inputEmail": self.patient.email,
            "inputPatientID": self.patient.id_number,
            "workerSelected": self.worker.email,
        }

        response = self.client.post('/register_appointment', PAST_TIME_APPOINTMENT, follow=True)

    def test_empty_fields_appointment(self, log_in, create_worker):
        EMPTY_WORKER_APPOINTMENT = {
            "inputDate": date.today().strftime("%x"),
            "inputTime": (datetime.now() - timedelta(hours=1)).strftime("%X"),
            "inputLastName": self.patient.last_name,
            "inputName": self.patient.name,
            "inputEmail": self.patient.email,
            "inputPatientID": self.patient.id_number,
            "workerSelected": "",
        }

        response = self.client.post('/register_appointment', EMPTY_WORKER_APPOINTMENT, follow=True)
