from django.test import RequestFactory
from django.test import Client
from django.urls import reverse

from appointments.models import Worker
from appointments.views import list_appointments
from appointments.views import register_appointment
from appointments.views import logout_view
from appointments.views import login_view

import pytest

from conftest import DEFAULT_USERNAME, DEFAULT_PASS, PASSWORD_KEY


@pytest.mark.django_db
class TestLogin:
    HTTP_REDIRECT_CODE = 302
    HTTP_OK_CODE = 200

    TEST_PATH_CODE = [
        ("list_appointments", HTTP_OK_CODE),
        ("register_appointment", HTTP_OK_CODE),
        ("logout", HTTP_REDIRECT_CODE)
    ]

    USERNAME_FIELD = "email"
    PASSWORD_FIELD = "password"

    GOOD_USER = {
        USERNAME_FIELD: DEFAULT_USERNAME,
        PASSWORD_FIELD: DEFAULT_PASS
    }

    BAD_CREDENTIALS = {
        "bad_pass": {
            USERNAME_FIELD: DEFAULT_USERNAME,
            PASSWORD_FIELD: "bad_pass"
        },
        "bad_mail": {
            USERNAME_FIELD: "bad@mail.com",
            PASSWORD_FIELD: DEFAULT_PASS
        },
        "bad_credentials": {
            USERNAME_FIELD: "bad@mail.com",
            PASSWORD_FIELD: "bad_pass"
        },
    }

    @pytest.mark.parametrize("path, expected_code", TEST_PATH_CODE)
    def test_allowed_access(self, logged_user, path, expected_code):
        real_path = reverse(path)
        client, user = logged_user()
        response = client.get(real_path)

        assert expected_code == response.status_code

    @pytest.mark.parametrize("path", TEST_PATH_CODE)
    def test_unallowed_access(self, path):
        real_path = reverse(path[0])
        client = Client()
        response = client.get(real_path)

        assert self.HTTP_REDIRECT_CODE == response.status_code

    def test_unsuccessful_login(self, create_user):
        user = create_user()
        client = Client()
        bad_pass = self.BAD_CREDENTIALS["bad_pass"][PASSWORD_KEY]
        response = client.login(username=user.email, password=bad_pass)

        assert response is False

    @pytest.mark.parametrize("bad_user_key", BAD_CREDENTIALS)
    def test_unexisting_users_login(self, bad_user_key):
        path = reverse('login')
        bad_user = self.BAD_CREDENTIALS[bad_user_key]
        factory = RequestFactory()
        request = factory.post(path, data=bad_user)

        # Notice that goo should be marked as unexisting
        # since the create_user fixture is not getting called in this test
        with pytest.raises(Worker.DoesNotExist):
            login_view(request)

    def test_five_attempts_blocked(self, create_user):
        default_user = create_user()
        client = Client()
        bad_pass = self.BAD_CREDENTIALS["bad_pass"]

        for attempt in range(0, 5):
            client.post('/login', bad_pass)

        user = Worker.objects.get(email=default_user.email)
        assert user.password_attempts == 5 and user.is_active is False

    def test_attempts_reset(self, create_user):
        default_user = create_user()
        client = Client()
        bad_pass = self.BAD_CREDENTIALS["bad_pass"]

        for attempt in range(0, 3):
            client.post('/login', bad_pass)

        client.post('/login', self.GOOD_USER)
        user = Worker.objects.get(email=default_user.email)
        assert user.password_attempts == 0 and user.is_active is True
