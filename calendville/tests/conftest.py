import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


PASSWORD_KEY = "password"
USERNAME_KEY = "email"
DEFAULT_USERNAME = "user@example.com"
DEFAULT_PASS = "strong-test-pass"


@pytest.fixture
def test_username():
    return DEFAULT_USERNAME


@pytest.fixture
def test_password():
    return DEFAULT_PASS


@pytest.fixture
def create_user(db, django_user_model, test_username, test_password):
    def make_user(**kwargs):
        kwargs[PASSWORD_KEY] = test_password
        if USERNAME_KEY not in kwargs:
            kwargs[USERNAME_KEY] = test_username
        # TODO: Check how to use create_user to login in both web and
        # testing environments, using superuser for now
        return django_user_model.objects.create_user(**kwargs)
    return make_user


@pytest.fixture
def logged_user(db, client, create_user, test_username, test_password):
    def make_auto_login(user=None):
        if user is None:
            user = create_user()
        client.login(username=test_username, password=test_password)
        return client, user
    return make_auto_login


@pytest.fixture
def firefox_driver():
    firefox_options = Options()
    firefox_options.headless = True
    driver = webdriver.Firefox(options=firefox_options)
    yield driver
    driver.quit()


@pytest.fixture
def logged_firefox(live_server, firefox_driver, create_user):
    def login_driver(user=None):
        if user is None:
            user = create_user()
        base_url = str(live_server)
        firefox_driver.get(base_url + "/login")
        login_input = firefox_driver.find_element_by_id("email")
        login_input.send_keys(user.email)
        password_input = firefox_driver.find_element_by_id("password")
        password_input.send_keys(DEFAULT_PASS)
        firefox_driver.find_element_by_id("submit").click()
        return firefox_driver, user, live_server
    return login_driver
