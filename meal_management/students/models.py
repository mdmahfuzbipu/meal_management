from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone

from datetime import date
from decimal import Decimal
from calendar import monthrange


def first_day_of_current_month():
    return date.today().replace(day=1)


class MealType(models.Model):
    name = models.CharField(max_length=30, unique=True)  # e.g., "Beef+Fish"
    cost_per_day = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return f"{self.name} ({self.cost_per_day} per day)"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=40)
    student_id = models.CharField(max_length=16, unique=True)
    room = models.IntegerField()
    department = models.CharField(max_length=4)
    floor = models.CharField(max_length=10)
    batch = models.CharField(max_length=5)

    phone_number = models.CharField(max_length=15)
    email = models.EmailField()

    default_meal_type = models.ForeignKey(MealType, on_delete=models.CASCADE)

    class Meta:
        ordering = ["room", "name"]

    def __str__(self):
        return f"{self.name} (Room {self.room})"


class DailyMealStatus(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.BooleanField(default=True)  # True means ON

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ("student", "date")
        indexes = [
            models.Index(fields=['student', 'date']),
        ]

    def __str__(self):
        return f"{self.student.name} - {self.date} - {'ON' if self.status else 'OFF'}"


class MonthlyMealType(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    month = models.DateField(default=first_day_of_current_month)  # e.g., 2025-05-01
    meal_type = models.ForeignKey(MealType, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "month")

    def __str__(self):
        return f"{self.student.name} - {self.month.strftime('%B %Y')} - {self.meal_type.name}"


class WeeklyMealCost(models.Model):
    WEEKDAYS = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]
    weekday = models.IntegerField(choices=WEEKDAYS, unique=True)
    cost = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return f"{self.get_weekday_display()}: {self.cost} Tk"


class MonthlyMealSummary(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    month = models.DateField(default=first_day_of_current_month)

    staff_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    days_meal_consumed = models.PositiveIntegerField(default=0)
    actual_meal_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_meal_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    meal_type = models.ForeignKey(MealType, on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "month")

    def save(self, *args, **kwargs):
        if self.month > timezone.now().date().replace(day=1):
            return  # Abort saving if the summary month is in the future

        # Determine meal type
        monthly_type = MonthlyMealType.objects.filter(
            student=self.student, month=self.month
        ).first()
        self.meal_type = (
            monthly_type.meal_type if monthly_type else self.student.default_meal_type
        )

        # Count meal days and calculate cost
        year = self.month.year
        month = self.month.month
        num_days = monthrange(year, month)[1]

        meal_days = 0
        total_cost = Decimal(0)

        weekly_costs = {wc.weekday: wc.cost for wc in WeeklyMealCost.objects.all()}

        for day in range(1, num_days + 1):
            current_date = date(year, month, day)
            weekday = current_date.weekday()

            try:
                status = DailyMealStatus.objects.get(
                    student=self.student, date=current_date
                )
                if status.status:
                    meal_days += 1
                    cost = weekly_costs.get(weekday)
                    if cost:
                        total_cost += cost
            except DailyMealStatus.DoesNotExist:
                continue

        self.days_meal_consumed = meal_days
        self.actual_meal_cost = total_cost
        self.total_meal_cost = total_cost + self.staff_cost + self.other_costs

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.name} - {self.month.strftime('%B %Y')} Summary"


# class MonthlyMealSummary(models.Model):
#     student = models.ForeignKey(Student, on_delete=models.CASCADE)
#     month = models.DateField(default=lambda:date.today().replace(day=1))

#     staff_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     other_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0)

#     class Meta:
#         unique_together = ("student", "month")

#     @property
#     def days_meal_consumed(self):
#         return DailyMealStatus.objects.filter(
#             student=self.student,
#             date__year=self.month.year,
#             date__month=self.month.month,
#             status=True,
#         ).count()

#     @property
#     def meal_type(self):
#         meal_type_obj = MonthlyMealType.objects.filter(
#             student=self.student, month=self.month
#         ).first()

#         if meal_type_obj:
#             return meal_type_obj.meal_type

#         return self.student.default_meal_type

#     @property
#     def actual_meal_cost(self):
#         meal_type = self.meal_type
#         if meal_type:
#             return Decimal(self.days_meal_consumed) * meal_type.cost_per_day

#     @property
#     def total_meal_cost(self):
#         return self.actual_meal_cost + self.staff_cost + self.other_costs

#     def __str__(self):
#         return f"{self.student.name} - {self.month.strftime('%B %Y')} Summary"


# class ManagerView(models.Model):
#     student = models.OneToOneField(Student, on_delete=models.CASCADE)
#     student_meal_status = models.BooleanField(default=True)
#     meal_type = models.IntegerField()
