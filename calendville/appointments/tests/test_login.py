from django.test import RequestFactory
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser, User

from appointments.views import list_appointments
from appointments.views import logout_view

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

    TEST_USER = {
        "username": "good_user",
        "password": "good_pass"
    }

    BAD_CREDENTIALS = [
        {
            "username": "good_user",
            "password": "bad_pass"
        },
        {
            "username": "bad_user",
            "password": "good_pass"
        },
        {
            "username": "bad_user",
            "password": "bad_pass"
        },
    ]

    @pytest.mark.parametrize("url_name, func", ACCESS_URLS)
    def test_allowed_access(self, url_name, func):
        path = reverse(url_name)
        request = RequestFactory().get(path)
        request.user = mixer.blend(User)

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
        return User.objects.create_user(**self.TEST_USER)

    def test_successful_login(self, new_user):
        client = Client()
        response = client.post("/login", self.TEST_USER, follow=True)
        assert response.context["user"].is_authenticated is True

    @pytest.mark.parametrize("bad_user", BAD_CREDENTIALS)
    def test_unsuccessful_login(self, new_user, bad_user):
        client = Client()
        response = client.post("/login", bad_user, follow=True)
        assert response.context["user"].is_authenticated is False

    def test_five_attempts_blocked(self, new_user):
        client = Client()
        bad_pass_user = self.BAD_CREDENTIALS[0]
        for attempt in range(0, 5):
            client.post("/login", bad_pass_user, follow=True)

        response = client.post("/login", self.TEST_USER, follow=True)
        assert response.context["user"].is_authenticated is False
