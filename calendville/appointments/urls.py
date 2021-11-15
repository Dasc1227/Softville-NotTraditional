from django.urls import path

from appointments import views

urlpatterns = [
    path('index', views.index, name="index")
]
