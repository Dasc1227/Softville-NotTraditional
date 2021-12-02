from datetime import datetime, timedelta

import pytest

from appointments.models import Appointment, Worker, Patient

LIST_APPOINTMENTS_PATH = "/appointments"


@pytest.fixture
def browser_in_list(logged_firefox):
    driver, user, server = logged_firefox()

    def move_to_list():
        driver.get(str(server) + LIST_APPOINTMENTS_PATH)
        return driver, user, server
    return move_to_list


class TestNavigation:
    ACCESS_LINK_IDS = [
        "appointments-top-link",
        "appointments-link"
    ]

    @pytest.mark.parametrize("element_id", ACCESS_LINK_IDS)
    def test_access_from_main_menu(self, logged_firefox, element_id):
        driver, user, server = logged_firefox()
        list_link = driver.find_element_by_id(element_id)
        list_link.click()
        assert driver.current_url.endswith(LIST_APPOINTMENTS_PATH)


class TestListIntegrity:

    REGISTER_URL = "/register_appointment"

    APPOINTMENT_FIELDS = [
        "patient-name",
        "appointment-date",
        "appointment-doctor",
        "appointment-secretary"
    ]

    WORKERS = {
        "worker_1": {
            "email": "as@test.com",
            "id_number": "123456789",
            "id_type": "PH",
            "first_name": "Steven",
            "last_name": "Herrera",
        }
    }

    PATIENTS = {
        "patient_1": {
            "id_number": "11899483",
            "name": "Jose",
            "last_name": "Ramirez",
            "email": "jose@gmail.com"
        }
    }

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
        self.patient_1 = Patient.objects.create(
            id_number=self.PATIENTS['patient_1']['id_number'],
            name=self.PATIENTS['patient_1']['name'],
            last_name=self.PATIENTS['patient_1']['last_name'],
            email=self.PATIENTS['patient_1']['email']
        )

        self.valid_appointment = {
            "date": (datetime.now() + timedelta(days=1)).strftime("%x"),
            "time": datetime.now().strftime("%X"),
            "attended_by": self.worker_1.pk,
            "patient_id": self.patient_1.pk,
        }
        self.client.post(self.REGISTER_URL, self.valid_appointment, follow=True)

    def test_weekday_cards_visible(self, setup, browser_in_list):
        driver, user, server = browser_in_list()
        assert driver.find_element_by_id("weekday-label")

    @pytest.mark.parametrize("field", APPOINTMENT_FIELDS)
    def test_appointment_visible(self, setup, browser_in_list, field):
        driver, user, server = browser_in_list()
        assert driver.find_element_by_id(field)

