from datetime import datetime, timedelta, date

from django.test import RequestFactory
from django.test import Client
from django.urls import reverse

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
            "inputDate": date.today() + timedelta(days=1),
            "inputTime": datetime.now().strftime("%X"),
            "inputLastName": self.patient.last_name,
            "inputName": self.patient.name,
            "inputEmail": self.patient.email,
            "inputPatientID": self.patient.id_number,
            "workerSelected": self.worker.email,
        }

        response = self.client.post('/register_appointment', VALID_APPOINTMENT, follow=True)
        assert self.HTTP_OK_CODE == response.status_code



