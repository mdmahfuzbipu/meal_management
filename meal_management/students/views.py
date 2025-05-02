from django.shortcuts import render,redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from datetime import timedelta, time, datetime, date

from .models import Student, DailyMealStatus, MonthlyMealType,MonthlyMealSummary
from .forms import MealTypeChangeForm

# Create your views here.


@login_required
def student_dashboard(request):
    student = get_object_or_404(Student, user=request.user)
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)

    current_meal_type = MonthlyMealType.objects.filter(
        student=student,
        month=today.replace(day=1)
    ).first()
    
    today_status = DailyMealStatus.objects.filter(student=student, date=today).first()
    tomorrow_status = DailyMealStatus.objects.filter(student=student, date=tomorrow).first()
    
    return render(request, 'students/student_dashboard.html', {
        'student':student,
        'current_meal_type': current_meal_type,
        'today_status': today_status,
        'tomorrow_status': tomorrow_status,
    })
    
@login_required
def view_meal_summary(request):
    student = get_object_or_404(Student, user=request.user)
    
    try:
        summary = MonthlyMealSummary.objects.get(student=student)
    except MonthlyMealSummary.DoesNotExist:
        messages.warning(request, "Meal summary not found.")
        return redirect("student_dashboard")
    
    return render(request, "students/meal_summary.html",{
        "summary": summary,
    })
        

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
    
    
    
@login_required
def show_current_meal_type(request):
    student = get_object_or_404(Student, user=request.user)
    
    today = date.today()
    
    first_of_month = today.replace(day=1)
    
    current_type = MonthlyMealType.objects.get(student=student, month=first_of_month).meal_type
    
    return render(request, "students/current_meal_type.html", {"meal_type": current_type})


@login_required
def change_meal_type(request):
    user = request.user
    student = user.student
    
    now = timezone.now()
    today = now.date()
    
    first_day_next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
    last_day_of_month = first_day_next_month - timedelta(days=1)
    
    
    cutoff_time = datetime.combine(last_day_of_month, datetime.strptime("18:00", "%H:%M").time())
    cutoff_time = timezone.make_aware(cutoff_time)
    
    
    if timezone.now() > cutoff_time:
        messages.error(request, "You cannot change meal type after 6:00 PM on the last day of the month.")
        return redirect("change_meal_type")
    
    if request.method == "POST":
        form = MealTypeChangeForm(request.POST)
        if form.is_valid():
            meal_type = form.cleaned_data["meal_type"]
            
            meal_month = first_day_next_month
            
            obj, created = MonthlyMealType.objects.get_or_create(
                student=student,
                month=meal_month,
                defaults={"meal_type": meal_type}
            )
            
            if not created:
                obj.meal_type = meal_type
                obj.save()
                
            
            messages.success(request, "Meal type updated for next month")
            return redirect("change_meal_type")
    
    else:
        form = MealTypeChangeForm()
        
    return render(request, "students/change_meal_type.html", {
        "form": form,
        "cutoff_time": cutoff_time
    })



# def change_monthly_meal(request):
#     student = get_object_or_404(Student, user=request.user)
#     today = date.today()
#     next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    
#     if request.method == "POST":
#         form = MealTypeChangeForm(request.POST)
#         if form.is_valid():
#             meal_type = form.cleaned_data["meal_type"]
#             obj, created = MonthlyMealType.objects.update_or_create(
#                 student=student,
#                 month=next_month,
#                 defaults={"meal_type": meal_type}
#             )
            
#             messages.success(request, "Meal type updated for next month.")
#             return redirect("current_meal_type")
        
#         else:
#             form = MealTypeChangeForm()
        
#         return render(request, "students/change_meal_type.html",{
#             "form":form,
#             "next_month": next_month.strftime("%B %Y")
#         })
            