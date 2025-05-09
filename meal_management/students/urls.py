from django.urls import path
from .views import toggle_meal_status, show_current_meal_type, change_meal_type, student_dashboard, view_meal_summary, meal_history

urlpatterns = [
    path("dashboard/", student_dashboard, name="student_dashboard"),
    path("toggle-meal/", toggle_meal_status, name="meal_toggle"),
    path("meal-type/", show_current_meal_type, name="current_meal_type"),
    path("change-meal-type/", change_meal_type, name="change_meal_type"),
    path("meal-summary/", view_meal_summary, name="meal_summary"),
    path("meal-history/",meal_history, name="meal_history"),
]