from django.urls import path
from .views import toggle_meal_status

urlpatterns = [
    path("toggle-meal/", toggle_meal_status, name="meal_status"),
]