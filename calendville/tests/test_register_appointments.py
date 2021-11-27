from datetime import datetime, timedelta, date
import pytest

from appointments.models import Patient, Worker, Appointment


@pytest.mark.django_db
class TestRegisterAppointments:

    REGISTER_URL = "/register_appointment"

    EMPTY_APPOINTMENT_FORMS = [
        ("date", {
            "time": (datetime.now() - timedelta(hours=1)).strftime("%X"),
            "attended_by": "as@test.com",
            "patient_id": "11899483",
        }),
        ("time", {
            "date": date.today().strftime("%x"),
            "attended_by": "as@test.com",
            "patient_id": "11899483",
        }),
        ("attended_by", {
            "date": date.today().strftime("%x"),
            "time": (datetime.now() - timedelta(hours=1)).strftime("%X"),
            "patient_id": "11899483",
        }),
        ("patient_id", {
            "date": date.today().strftime("%x"),
            "time": (datetime.now() - timedelta(hours=1)).strftime("%X"),
            "attended_by": "as@test.com",
        }),
    ]

    @pytest.fixture
    def setup(self, logged_user):
        self.client, self.user = logged_user()
        self.worker = Worker.objects.create(email="as@test.com", id_number="1234",
                                         id_type="PH", first_name="Steven",
                                         last_name="Herrera", is_staff=True,
                                         is_active=True)
        self.patient = Patient.objects.create(id_number="11899483", name="Patient",
                                           last_name="Patient",
                                           email="patient@test.com")

    def test_valid_appointment(self, setup):
        appointment_date = date.today() + timedelta(days=1)
        appointment_time = datetime.now()
        VALID_APPOINTMENT = {
            "date": appointment_date.strftime("%x"),
            "time": appointment_time.strftime("%X"),
            "attended_by": self.worker.pk,
            "patient_id": self.patient.pk,
        }
        self.client.post(self.REGISTER_URL, VALID_APPOINTMENT, follow=True)
        assert Appointment.objects.last().start_time, datetime.combine(appointment_date,
                                                                       appointment_time.time())

    def test_past_date_appointment(self, setup):
        PAST_DATE_APPOINTMENT = {
            "date": (date.today() - timedelta(days=1)).strftime("%x"),
            "time": datetime.now().strftime("%X"),
            "attended_by": self.worker.pk,
            "patient_id": self.patient.pk,
        }

        response = self.client.post(self.REGISTER_URL, PAST_DATE_APPOINTMENT, follow=True)
        assert "date" in response.context['form'].errors

    def test_past_time_appointment(self, setup):
        PAST_TIME_APPOINTMENT = {
            "date": date.today().strftime("%x"),
            "time": (datetime.now() - timedelta(hours=1)).strftime("%X"),
            "attended_by": self.worker.pk,
            "patient_id": self.patient.pk,
        }

        response = self.client.post(self.REGISTER_URL, PAST_TIME_APPOINTMENT, follow=True)
        assert "time" in response.context['form'].errors

    @pytest.mark.parametrize("missing_field, data", EMPTY_APPOINTMENT_FORMS)
    def test_empty_field_appointment(self, setup, missing_field, data):
        response = self.client.post(self.REGISTER_URL, data, follow=True)
        assert missing_field in response.context['form'].errors




