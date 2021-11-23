import pytest


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
        return django_user_model.objects.create_superuser(**kwargs)
    return make_user


@pytest.fixture
def logged_user(db, client, create_user, test_username, test_password):
    def make_auto_login(user=None):
        if user is None:
            user = create_user()
        client.login(username=test_username, password=test_password)
        return client, user
    return make_auto_login
