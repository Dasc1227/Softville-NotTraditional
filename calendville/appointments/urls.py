from django.urls import path

from appointments import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login', views.login_view, name="login"),
    path('logout', views.logout_view, name="logout"),
    path('register_appointment', views.register_appointment,
         name="register_appointment"),
    path('appointments', views.list_appointments,
         name="list_appointments"),
    path('procedures', views.list_health_procedures,
         name="health_procedures"),
    path('register_procedure', views.register_health_procedures,
         name="register_procedure"),
    path('register_patient', views.register_patient,
         name="register_patient")
]
