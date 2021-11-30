import pytest

from appointments.models import Patient


@pytest.mark.django_db
class TestRegisterPatient:
    REGISTER_URL = "/register_appointment"

    PATIENTS = {
        "patient_1": {
            "id_number": "1111",
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
        "patient_3": {
            "id_number": "113427952",
            "name": "Pedro",
            "last_name": "Calderon",
            "email": "pedro@gmail.com"
        },
    }

    EMPTY_APPOINTMENT_FORMS = [
        ("name", {
            "id_number": PATIENTS['patient_2']['id_number'],
            "last_name": PATIENTS['patient_2']['last_name'],
            "email": PATIENTS['patient_2']['email'],
        }),
        ("last_name", {
            "id_number": PATIENTS['patient_2']['id_number'],
            "name": PATIENTS['patient_2']['name'],
            "email": PATIENTS['patient_2']['email'],
        }),
        ("email", {
            "id_number": PATIENTS['patient_2']['id_number'],
            "last_name": PATIENTS['patient_2']['last_name'],
            "name": PATIENTS['patient_2']['name'],
        }),
        ("id_number", {
            "name": PATIENTS['patient_2']['name'],
            "last_name": PATIENTS['patient_2']['last_name'],
            "email": PATIENTS['patient_2']['email'],
        }),
    ]

    @pytest.fixture
    def setup(self, logged_user):
        self.client, self.user = logged_user()

    # TODO: Skipping since this functionality is not implemented yet
    @pytest.mark.skip
    def test_valid_id(self, setup):
        self.client.post(self.REGISTER_URL, self.PATIENTS['patient_2'],
                         follow=True)
        valid_patient_id = self.PATIENTS['patient_2']['id_number']
        query = Patient.objects.filter(id_number=valid_patient_id)              
        assert len(query) == 1

    # TODO: Skipping since this functionality is not implemented yet
    @pytest.mark.skip
    def test_invalid_id(self, setup):
        response = self.client.post(self.REGISTER_URL,
                                    self.PATIENTS['patient_1'],
                                    follow=True)          
        assert "patient_id" in response.context['form'].errors

    # TODO: Skipping since this functionality is not implemented yet    
    @pytest.mark.skip
    def test_repeat_id(self, setup):
        self.patient_2 = Patient.objects.create(
            id_number=self.PATIENTS['patient_2']['id_number'],
            name=self.PATIENTS['patient_2']['name'],
            last_name=self.PATIENTS['patient_2']['last_name'],
            email=self.PATIENTS['patient_2']['email']
        )
        response = self.client.post(self.REGISTER_URL,
                                    self.PATIENTS['patient_3'],
                                    follow=True)         
        assert "patient_id" in response.context['form'].errors

    # TODO: Skipping since this functionality is not implemented yet
    @pytest.mark.skip
    @pytest.mark.parametrize("missing_field, data", EMPTY_APPOINTMENT_FORMS)
    def test_empty_field_patient(self, setup, missing_field, data):
        response = self.client.post(self.REGISTER_URL, data, follow=True)
        assert missing_field in response.context['form'].errors       
