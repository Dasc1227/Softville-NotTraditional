from django.urls import path

from calendar import views

urlpatterns = [
    path('index', views.index, name="index")
]