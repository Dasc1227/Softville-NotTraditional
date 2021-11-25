
class TestWithSelenium:
    def test_logged_fixture(self, logged_firefox):
        driver, user, server = logged_firefox()
        assert driver.find_element_by_id("main-container") is not None
