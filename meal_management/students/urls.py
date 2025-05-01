from django.urls import path
from .views import toggle_meal_status, show_current_meal_type, change_monthly_meal

urlpatterns = [
    path("toggle-meal/", toggle_meal_status, name="meal_status"),
    path("meal-type", show_current_meal_type, name="current_meal_type"),
    path("meal-type/change/", change_monthly_meal, name="change_meal_type"),
]