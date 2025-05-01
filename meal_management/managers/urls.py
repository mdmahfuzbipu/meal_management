from django.urls import path
from .views import search_by_room, trigger_meal_count, daily_meal_stats_view

urlpatterns = [
    path('search/', search_by_room, name="manager_search"),
    path('trigger-meal-count/',trigger_meal_count, name="trigger_meal_count"),
    path('stats/', daily_meal_stats_view, name="daily_meal_stats")
]