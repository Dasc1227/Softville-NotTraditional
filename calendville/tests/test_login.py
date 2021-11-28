from django.urls import reverse

from appointments.models import Worker

import pytest

from conftest import DEFAULT_USERNAME, DEFAULT_PASS


@pytest.mark.django_db
class TestLogin:
    HTTP_REDIRECT_CODE = 302
    HTTP_OK_CODE = 200

    TEST_PATH_CODE = [
        ("list_appointments", HTTP_OK_CODE),
        ("index", HTTP_OK_CODE),
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
    def test_unallowed_access(self, path, client):
        real_path = reverse(path[0])
        response = client.get(real_path)

        assert self.HTTP_REDIRECT_CODE == response.status_code

    @pytest.mark.parametrize("path", TEST_PATH_CODE)
    def test_custom_url_login(self, path, create_user, client):
        new_url = reverse(path[0])
        data = {
            "email": DEFAULT_USERNAME,
            "password": DEFAULT_PASS,
            "next": new_url
        }
        path = reverse('login') + "?next=" + new_url
        create_user()
        response = client.post(path, data)
        assert new_url == response.headers["Location"]

    def test_unsuccessful_login(self, create_user, client):
        path = reverse('login')
        create_user()
        bad_pass = self.BAD_CREDENTIALS["bad_pass"]
        response = client.post(path, bad_pass)

        assert "Contraseña inválida" in response.context["error"]

    @pytest.mark.parametrize("bad_user_key", BAD_CREDENTIALS)
    def test_unexisting_users_login(self, bad_user_key, client):
        path = reverse('login')
        bad_user = self.BAD_CREDENTIALS[bad_user_key]
        response = client.post(path, bad_user)
        assert "no existe" in response.context["error"]

    def test_no_user_normal_login_form(self, client):
        path = reverse("login")
        response = client.get(path)
        assert self.HTTP_OK_CODE == response.status_code

    def test_redirect_when_accesing_login(self, logged_user):
        path = reverse("login")
        client, user = logged_user()
        response = client.get(path)

        assert self.HTTP_REDIRECT_CODE == response.status_code

    def test_five_attempts_blocked(self, create_user, client):
        default_user = create_user()
        bad_pass = self.BAD_CREDENTIALS["bad_pass"]

        for attempt in range(0, 5):
            client.post('/login', bad_pass)

        user = Worker.objects.get(email=default_user.email)
        assert user.password_attempts == 5 and user.is_active is False

    def test_attempts_reset(self, create_user, client):
        default_user = create_user()
        bad_pass = self.BAD_CREDENTIALS["bad_pass"]

        for attempt in range(0, 3):
            client.post('/login', bad_pass)

        client.post('/login', self.GOOD_USER)
        user = Worker.objects.get(email=default_user.email)
        assert user.password_attempts == 0 and user.is_active is True
