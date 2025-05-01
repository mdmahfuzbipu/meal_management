from django.shortcuts import render,redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta, time
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from datetime import date, timedelta


from .models import Student, DailyMealStatus, MonthlyMealType
from .forms import MealTypeChangeForm

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
    
    
    
    
def show_current_meal_type(request):
    student = get_object_or_404(Student, user=request.user)
    
    today = date.today()
    
    first_of_month = today.replace(day=1)
    
    current_type = MonthlyMealType.objects.get(student=student, month=first_of_month).meal_type
    
    return render(request, "students/current_meal_type.html", {"meal_type": current_type})



def change_monthly_meal(request):
    student = get_object_or_404(Student, user=request.user)
    today = date.today()
    next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    
    if request.method == "POST":
        form = MealTypeChangeForm(request.POST)
        if form.is_valid():
            meal_type = form.cleaned_data["meal_type"]
            obj, created = MonthlyMealType.objects.update_or_create(
                student=student,
                month=next_month,
                defaults={"meal_type": meal_type}
            )
            
            messages.success(request, "Meal type updated for next month.")
            return redirect("current_meal_type")
        
        else:
            form = MealTypeChangeForm()
        
        return render(request, "students/change_meal_type.html",{
            "form":form,
            "next_month": next_month.strftime("%B %Y")
        })
            