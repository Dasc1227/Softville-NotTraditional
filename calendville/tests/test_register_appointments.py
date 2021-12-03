from datetime import datetime, timedelta, date, time
import pytest

from appointments.models import Patient, Worker, Appointment


@pytest.mark.django_db
class TestRegisterAppointments:

    REGISTER_URL = "/register_appointment"

    WORKERS = {
        "worker_1": {
            "email": "as@test.com",
            "id_number": "123456789",
            "id_type": "PH",
            "first_name": "Steven",
            "last_name": "Herrera",
        },
        "worker_2": {
            "email": "bd@test.com",
            "id_number": "987654321",
            "id_type": "PH",
            "first_name": "Luis",
            "last_name": "Ramírez",
        }
    }

    PATIENTS = {
        "patient_1": {
            "id_number": "11899483",
            "name": "Jose",
            "last_name": "Ramirez",
            "email": "jose@gmail.com"
        },
        "patient_2": {
            "id_number": "113427952",
            "name": "Pedro",
            "last_name": "Calderon",
            "email": "pedro@gmail.com"
        },
    }

    EMPTY_APPOINTMENT_FORMS = [
        ("date", {
            "time": (datetime.now() - timedelta(hours=1)).strftime("%X"),
            "attended_by": WORKERS['worker_1']['email'],
            "patient_id": PATIENTS['patient_1']['id_number'],
        }),
        ("time", {
            "date": date.today().strftime("%x"),
            "attended_by": WORKERS['worker_1']['email'],
            "patient_id": PATIENTS['patient_1']['id_number'],
        }),
        ("attended_by", {
            "date": date.today().strftime("%x"),
            "time": (datetime.now() - timedelta(hours=1)).strftime("%X"),
            "patient_id": PATIENTS['patient_1']['id_number'],
        }),
        ("patient_id", {
            "date": date.today().strftime("%x"),
            "time": (datetime.now() - timedelta(hours=1)).strftime("%X"),
            "attended_by": WORKERS['worker_1']['email'],
        }),
    ]

    @pytest.fixture
    def setup(self, logged_user):
        self.client, self.user = logged_user()

        self.worker_1 = Worker.objects.create(
            email=self.WORKERS['worker_1']['email'],
            id_number=self.WORKERS['worker_1']['id_number'],
            id_type=self.WORKERS['worker_1']['id_type'],
            first_name=self.WORKERS['worker_1']['first_name'],
            last_name=self.WORKERS['worker_1']['last_name'],
            is_staff=True,
            is_active=True
        )

        self.worker_2 = Worker.objects.create(
            email=self.WORKERS['worker_2']['email'],
            id_number=self.WORKERS['worker_2']['id_number'],
            id_type=self.WORKERS['worker_2']['id_type'],
            first_name=self.WORKERS['worker_2']['first_name'],
            last_name=self.WORKERS['worker_2']['last_name'],
            is_staff=True,
            is_active=True
        )

        self.patient_1 = Patient.objects.create(
            id_number=self.PATIENTS['patient_1']['id_number'],
            name=self.PATIENTS['patient_1']['name'],
            last_name=self.PATIENTS['patient_1']['last_name'],
            email=self.PATIENTS['patient_1']['email']
        )

        self.patient_2 = Patient.objects.create(
            id_number=self.PATIENTS['patient_2']['id_number'],
            name=self.PATIENTS['patient_2']['name'],
            last_name=self.PATIENTS['patient_2']['last_name'],
            email=self.PATIENTS['patient_2']['email']
        )

    def get_appointment(self, appointment_date,
                        appointment_time,
                        worker,
                        patient):
        valid_appointment = {
            "date": appointment_date.strftime("%x"),
            "time": appointment_time.strftime("%X"),
            "attended_by": worker.pk,
            "patient_id": patient.pk,
        }
        return valid_appointment

    def test_valid_appointment(self, setup):
        appointment_date = date.today() + timedelta(days=1)
        appointment_time = datetime.combine(appointment_date, time(12, 0, 0))
        valid_appointment = self.get_appointment(appointment_date,
                                                 appointment_time,
                                                 self.worker_1,
                                                 self.patient_1)
        self.client.post(self.REGISTER_URL, valid_appointment, follow=True)
        appointment_datetime = Appointment.objects.last().start_time
        assert appointment_datetime, datetime.combine(appointment_date,
                                                      appointment_time.time())

    def test_past_date_appointment(self, setup):
        appointment_date = date.today() - timedelta(days=1)
        appointment_time = datetime.combine(appointment_date, time(12, 0, 0))
        past_date_appointment = self.get_appointment(appointment_date,
                                                     appointment_time,
                                                     self.worker_1,
                                                     self.patient_1)
        response = self.client.post(self.REGISTER_URL,
                                    past_date_appointment,
                                    follow=True)
        assert "date" in response.context['form'].errors

    def test_past_time_appointment(self, setup):
        appointment_date = date.today()
        appointment_time = datetime.now() - timedelta(hours=1)
        past_time_appointment = self.get_appointment(appointment_date,
                                                     appointment_time,
                                                     self.worker_1,
                                                     self.patient_1)
        response = self.client.post(self.REGISTER_URL,
                                    past_time_appointment,
                                    follow=True)
        assert "time" in response.context['form'].errors

    @pytest.mark.parametrize("missing_field, data", EMPTY_APPOINTMENT_FORMS)
    def test_empty_field_appointment(self, setup, missing_field, data):
        response = self.client.post(self.REGISTER_URL, data, follow=True)
        assert missing_field in response.context['form'].errors

    def test_overlapped_appointment_for_doctor(self, setup):
        appointment_date = date.today() + timedelta(days=1)
        appointment_time = datetime.combine(appointment_date, time(12, 0, 0))
        overlapped_time = appointment_time + timedelta(minutes=59)
        appointment = self.get_appointment(appointment_date,
                                           appointment_time,
                                           self.worker_1,
                                           self.patient_1)
        overlapped_appointment = self.get_appointment(appointment_date,
                                                      overlapped_time,
                                                      self.worker_1,
                                                      self.patient_2)
        self.client.post(self.REGISTER_URL, appointment, follow=True)
        response = self.client.post(self.REGISTER_URL,
                                    overlapped_appointment,
                                    follow=True)
        assert "attended_by" in response.context['form'].errors

    def test_overlapped_appointment_for_patient(self, setup):
        appointment_date = date.today() + timedelta(days=1)
        appointment_time = datetime.combine(appointment_date, time(12, 0, 0))
        overlapped_time = appointment_time + timedelta(minutes=59)
        appointment = self.get_appointment(appointment_date,
                                           appointment_time,
                                           self.worker_1,
                                           self.patient_1)
        overlapped_appointment = self.get_appointment(appointment_date,
                                                      overlapped_time,
                                                      self.worker_2,
                                                      self.patient_1)

        self.client.post(self.REGISTER_URL, appointment, follow=True)
        response = self.client.post(self.REGISTER_URL,
                                    overlapped_appointment,
                                    follow=True)
        assert "patient_id" in response.context['form'].errors

    def test_no_work_hours_appointment(self, setup):
        appointment_date = date.today()
        appointment_time = datetime.combine(appointment_date, time(8, 0, 0))
        no_work_hour_appointment = self.get_appointment(appointment_date,
                                                        appointment_time,
                                                        self.worker_1,
                                                        self.patient_1)
        response = self.client.post(self.REGISTER_URL,
                                    no_work_hour_appointment,
                                    follow=True)
        assert "time" in response.context['form'].errors
