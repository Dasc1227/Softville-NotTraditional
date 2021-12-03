import pytest

PROCEDURES_PATH = "/procedures"


@pytest.fixture
def browser_in_form(logged_firefox):
    driver, user, server = logged_firefox()

    def move_to_form():
        driver.get(str(server) + PROCEDURES_PATH)
        return driver, user, server
    return move_to_form


class TestListNavigation:
    ACCESS_LINK_IDS = [
        "procedures-top-link",
        "procedures-link"
    ]

    @pytest.mark.parametrize("element_id", ACCESS_LINK_IDS)
    def test_access_from_main_menu(self, logged_firefox, element_id):
        driver, user, server = logged_firefox()
        list_link = driver.find_element_by_id(element_id)
        list_link.click()
        assert driver.current_url.endswith(PROCEDURES_PATH)


class TestListFormIntegrity:
    SEARCH_FIELD_NAMES = [
        "query-input",
        "submit-button"
    ]

    @pytest.mark.parametrize("field", SEARCH_FIELD_NAMES)
    def test_field_available(self, browser_in_form, field):
        driver, user, server = browser_in_form()
        assert driver.find_element_by_id(field)
