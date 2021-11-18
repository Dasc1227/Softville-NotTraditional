from django.test import RequestFactory
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser

from appointments.models import Worker
from appointments.views import list_appointments
from appointments.views import logout_view
from appointments.views import login_view

from mixer.backend.django import mixer

import pytest


@pytest.mark.django_db
class TestLogin:
    HTTP_REDIRECT_CODE = 302
    HTTP_OK_CODE = 200
    ACCESS_URLS = [
        ("list_appointments", list_appointments),
        ("logout", logout_view)
    ]

    USERNAME_FIELD = "email"
    PASSWORD_FIELD = "password"

    GOOD_USER = {
        USERNAME_FIELD: "good@mail.com",
        PASSWORD_FIELD: "good_pass"
    }

    BAD_CREDENTIALS = [
        {
            USERNAME_FIELD: "good@mail.com",
            PASSWORD_FIELD: "bad_pass"
        },
        {
            USERNAME_FIELD: "bad@mail.com",
            PASSWORD_FIELD: "good_pass"
        },
        {
            USERNAME_FIELD: "bad@mail.com",
            PASSWORD_FIELD: "bad_pass"
        },
    ]

    @pytest.mark.parametrize("url_name, func", ACCESS_URLS)
    def test_allowed_access(self, url_name, func):
        path = reverse(url_name)
        request = RequestFactory().get(path)
        request.user = mixer.blend(Worker)

        response = func(request)
        assert self.HTTP_OK_CODE == response.status_code

    @pytest.mark.parametrize("url_name, func", ACCESS_URLS)
    def test_unallowed_access(self, url_name, func):
        path = reverse(url_name)
        request = RequestFactory().get(path)
        request.user = AnonymousUser()
        response = func(request)

        assert self.HTTP_REDIRECT_CODE == response.status_code

    @pytest.fixture
    def new_user(self):
        return Worker.objects.create_user(**self.GOOD_USER)

    def test_successful_login(self, new_user):
        client = Client()
        response = client.post("/login", self.GOOD_USER, follow=True)
        assert response.context["user"].is_active is True

    def test_unsuccessful_login(self, new_user):
        client = Client()
        bad_pass_user = self.BAD_CREDENTIALS[0]
        response = client.post("/login", bad_pass_user, follow=True)

        assert response.context["user"].is_authenticated is False

    @pytest.mark.parametrize("bad_user", BAD_CREDENTIALS)
    def test_unexisting_users_login(self, bad_user):
        path = reverse('login')
        factory = RequestFactory()
        request = factory.post(path, data=bad_user)

        # Notice that good@mail.com should be marked as unexisting
        # since the new_user fixture is not getting called in this test
        with pytest.raises(Worker.DoesNotExist):
            login_view(request)

    def test_five_attempts_blocked(self, new_user):
        client = Client()
        bad_pass_user = self.BAD_CREDENTIALS[0]
        for attempt in range(0, 5):
            client.post("/login", bad_pass_user, follow=True)

        response = client.post("/login", self.GOOD_USER, follow=True)
        assert response.context["user"].is_authenticated is False
