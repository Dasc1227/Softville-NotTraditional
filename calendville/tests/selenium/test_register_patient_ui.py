import pytest

REGISTER_PATIENTS_PATH = "/register_patient"


@pytest.fixture
def browser_in_form(logged_firefox):
    driver, user, server = logged_firefox()

    def move_to_form():
        driver.get(str(server) + REGISTER_PATIENTS_PATH)
        return driver, user, server
    return move_to_form


class TestFormIntegrity:
    INPUT_FIELD_IDS = [
        "csrfmiddlewaretoken",
        "id_number",
        "name",
        "last_name",
        "email",
        "submit_button"
    ]

    REQUIRED_FIELDS = []

    def get_required_fields(fields_list):
        fields = fields_list.copy()
        fields.remove("csrfmiddlewaretoken")
        fields.remove("submit_button")
        return fields

    @pytest.mark.parametrize("field", INPUT_FIELD_IDS)
    def test_field_available(self, browser_in_form, field):
        driver, user, server = browser_in_form()
        assert driver.find_element_by_name(field)

    @pytest.mark.parametrize("field", get_required_fields(INPUT_FIELD_IDS))
    def test_field_is_required(self, browser_in_form, field):
        driver, user, server = browser_in_form()
        input_field = driver.find_element_by_name(field)
        assert input_field.get_attribute("required")
