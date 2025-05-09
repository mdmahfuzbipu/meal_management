from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import make_aware,get_current_timezone

from datetime import timedelta, time, datetime, date

from .models import Student, DailyMealStatus, MonthlyMealType, MonthlyMealSummary
from .forms import MealTypeChangeForm

# Create your views here.


@login_required
def student_dashboard(request):
    student = get_object_or_404(Student, user=request.user)
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)

    current_month = today.replace(day=1)
    next_month = (current_month + timedelta(32)).replace(day=1)
    
    #current meal type
    monthly_type = MonthlyMealType.objects.filter(student=student, month=current_month).first()
    current_meal_type = monthly_type.meal_type if monthly_type else student.default_meal_type
    
    #next month meal type
    next_monthly_type = MonthlyMealType.objects.filter(student=student, month=next_month).first()
    next_meal_type = next_monthly_type.meal_type if next_monthly_type else student.default_meal_type
    
    #today and tomorrow's meal status
    today_status_obj = DailyMealStatus.objects.filter(
        student=student,
        date=today
    ).first()
    
    today_status = today_status_obj.status if today_status_obj else True
    
    
    tomorrow_status_obj = DailyMealStatus.objects.filter(
        student=student, date=tomorrow
    ).first()
    
    tomorrow_status = tomorrow_status_obj.status if tomorrow_status_obj else True

    return render(
        request,
        "students/student_dashboard.html",
        {
            "student": student,
            "current_meal_type": current_meal_type,
            "next_meal_type":next_meal_type,
            "today_status": today_status,
            "tomorrow_status": tomorrow_status,
        },
    )


@login_required
def view_meal_summary(request):
    student = request.user.student

    month_str = request.GET.get("month")
    if month_str:
        try:
            month = datetime.strptime(month_str, "%Y-%m").date().replace(day=1)
        except ValueError:
            month = date.today().replace(day=1)
    
    else:
        month = date.today().replace(day=1)
            

    summary, created = MonthlyMealSummary.objects.get_or_create(
        student=student, month=month
    )

    if created:
        summary.save()

    return render(request, "students/meal_summary.html", {
        "summary": summary,
        "selected_month": month,
        })


@login_required
def toggle_meal_status(request):
    student = Student.objects.get(user=request.user)
    tomorrow = timezone.now().date() + timedelta(days=1)

    if request.method == "POST":
        current_time = timezone.now().astimezone(get_current_timezone()).time()
        if current_time >= time(18, 0):
            messages.error(request, "You can't update meal status after 6:00 PM")
            return redirect("meal_toggle")

        status_obj, created = DailyMealStatus.objects.get_or_create(
            student=student, date=tomorrow
        )

        status_obj.status = not status_obj.status
        status_obj.save()
        messages.success(
            request,
            f"Meal turned {'ON' if status_obj.status else 'OFF'} for {tomorrow}",
        )
        return redirect("meal_toggle")

    status_obj = DailyMealStatus.objects.filter(student=student, date=tomorrow).first()

    return render(
        request,
        "students/meal_toggle.html",
        {
            "status": status_obj,
            "tomorrow": tomorrow,
        },
    )


@login_required
def show_current_meal_type(request):
    student = get_object_or_404(Student, user=request.user)

    today = date.today()

    first_of_month = today.replace(day=1)

    current_record = MonthlyMealType.objects.filter(
        student=student,
        month=first_of_month
    ).first()
    current_type = current_record.meal_type if current_record else None
    
    # current_type = MonthlyMealType.objects.get(
    #     student=student, month=first_of_month
    # ).meal_type

    return render(
        request, "students/current_meal_type.html", {"meal_type": current_type}
    )


@login_required
def change_meal_type(request):
    student = request.user.student

    now = timezone.now()
    today = now.date()

    first_day_next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
    last_day_of_month = first_day_next_month - timedelta(days=1)

    cutoff_time = make_aware(datetime.combine(last_day_of_month, time(18,0)), get_current_timezone())

    # cutoff_time = timezone.make_aware(
    #     datetime.combine(last_day_of_month, time(18,0))
    # )

    if now > cutoff_time:
        messages.error(
            request,
            "You cannot change meal type after 6:00 PM on the last day of the month.",
        )
        return redirect("change_meal_type")

    if request.method == "POST":
        form = MealTypeChangeForm(request.POST)
        if form.is_valid():
            meal_type = form.cleaned_data["meal_type"]

            obj, created = MonthlyMealType.objects.get_or_create(
                student=student, month=first_day_next_month, defaults={"meal_type": meal_type}
            )

            if not created:
                obj.meal_type = meal_type
                obj.save()

            messages.success(
                request,
                f"Meal type for {first_day_next_month.strftime('%B')} updated successfully.",
            )
            return redirect("student_dashboard")

    else:
        form = MealTypeChangeForm()

    return render(
        request,
        "students/change_meal_type.html",
        {"form": form, "cutoff_time": cutoff_time},
    )


def home(request):
    return render(request, "students/home.html")


@login_required
def meal_history(request):
    student = request.user.student

    month_str = request.GET.get("month")

    if month_str:
        try:
            first_day = datetime.strptime(month_str, "%Y-%m").date().replace(day=1)
        except ValueError:
            first_day = timezone.now().date().replace(day=1)

    else:
        first_day = timezone.now().date().replace(day=1)

    next_month = (first_day + timedelta(days=32)).replace(day=1)
    last_day = next_month - timedelta(days=1)
    
    statuses = DailyMealStatus.objects.filter(
        student=student,
        date__range = (first_day, last_day)
    ).order_by("date")

    return render(
        request,
        "students/meal_history.html",
        {
            "statuses": statuses,
            "selected_month" : first_day,
        }
    )

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
