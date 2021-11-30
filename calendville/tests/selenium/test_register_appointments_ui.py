import pytest

REGISTER_APPOINTMENTS_PATH = "/register_appointment"


@pytest.fixture
def browser_in_form(logged_firefox):
    driver, user, server = logged_firefox()

    def move_to_form():
        driver.get(str(server) + REGISTER_APPOINTMENTS_PATH)
        return driver, user, server
    return move_to_form


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
        register_link = driver.find_element_by_id("new-appointment-link")
        register_link.click()
        assert driver.current_url.endswith(REGISTER_APPOINTMENTS_PATH)


class TestFormIntegrity:
    INPUT_FIELD_IDS = [
        "csrfmiddlewaretoken",
        "date",
        "time",
        "attended_by",
        "patient_id",
        "submit_button"
    ]

    def remove_token(fields_list, token):
        fields = fields_list.copy()
        fields.remove(token)
        return fields

    @pytest.mark.parametrize("field", INPUT_FIELD_IDS)
    def test_field_available(self, browser_in_form, field):
        driver, user, server = browser_in_form()
        assert driver.find_element_by_name(field)

    @pytest.mark.parametrize("field", remove_token(INPUT_FIELD_IDS,
                                                   "csrfmiddlewaretoken"))
    def test_field_is_required(self, browser_in_form, field):
        driver, user, server = browser_in_form()
        input_field = driver.find_element_by_name(field)
        assert input_field.get_attribute("required")
