import pytest

AUTHENTICATION_PATH = "/login"


@pytest.fixture
def browser_in_form(firefox_driver, live_server):
    driver = firefox_driver()

    def move_to_form():
        driver.get(str(live_server) + AUTHENTICATION_PATH)
        return driver,  live_server
    return move_to_form


class TestFormIntegrity:
    INPUT_FIELD_IDS = [
        "email",
        "password",
        "submit",
        "next"
    ]

    REQUIRED_FIELDS = []

    def get_required_fields(fields_list):
        fields = fields_list.copy()
        fields.remove("submit")
        return fields

    @pytest.mark.skip
    @pytest.mark.parametrize("field", INPUT_FIELD_IDS)
    def test_field_available(self, browser_in_form, field):
        driver, live_server = browser_in_form()
        assert driver.find_element_by_name(field)

    @pytest.mark.skip
    @pytest.mark.parametrize("field", get_required_fields(INPUT_FIELD_IDS))
    def test_field_is_required(self, browser_in_form, field):
        driver, live_server = browser_in_form()
        input_field = driver.find_element_by_name(field)
        assert input_field.get_attribute("required")
