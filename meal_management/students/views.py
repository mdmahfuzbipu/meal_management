from django.shortcuts import render,redirect
from django.utils import timezone
from datetime import timedelta, time
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Student, DailyMealStatus


# Create your views here.

@login_required
def toggle_meal_status(request):
    student = Student.objects.get(user=request.user)
    tomorrow = timezone.now().date() + timedelta(days=1)
    
    
    if(timezone.now().time() >= time(18,0)):
        messages.error(request, "You can't update meal status after 6:00 PM")
        return redirect("meal_status")
    
    
    status_obj, created = DailyMealStatus.objects.get_or_create(
        student = student, date = tomorrow
    )
    
    if request.method == "POST":
        status_obj.status = not status_obj.status
        status_obj.save()
        messages.success(request, f"Meal turned {"ON" if status_obj.status else "OFF"} for {tomorrow}")
        return redirect("meal_status")
    
    return render(request, "students/meal_toggle.html",{
        "status": status_obj,
        "tomorrow": tomorrow,
    })