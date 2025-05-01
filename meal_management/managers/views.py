from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages


from students.models import Student, MealInfo
from .models import MealCount
from .utils import generate_meal_count
# Create your views here.

@staff_member_required
def daily_meal_stats_view(request):
    stats = MealCount.objects.order_by('-date')
    return render(request, "managers/daily_meal_stats.html", {'stats': stats})

@staff_member_required
def trigger_meal_count(request):
    generate_meal_count()
    return redirect('daily_meal_stats')


def search_by_room(request):
    students = []
    if 'room' in request.GET:
        room = request.GET['room']
        students = Student.objects.filter(room=room).select_related('mealinfo')
    return render(request, 'managers/manager_search.html', {'students':students})
