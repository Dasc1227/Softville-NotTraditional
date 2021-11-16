from django.urls import path

from appointments import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login', views.login_view, name="login"),
    path('logout', views.logout_view, name="logout"),
    path('register_appointment', views.register_appointment, name="register_appointment")
]
