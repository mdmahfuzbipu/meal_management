from django.db import models
from django.contrib.auth.models import User
from datetime import date



class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    room = models.IntegerField()  # 208
    name = models.CharField(max_length=40)
    student_id = models.CharField(max_length=16, unique=True)

    department = models.CharField(max_length=4)  # ICE, CSE
    floor = models.CharField(max_length=10)  # 2nd floor
    batch = models.CharField(max_length=5)  # 16th

    phone_number = models.CharField(max_length=15)
    email = models.EmailField()


    class Meta:
        ordering = ["room", "name"]

    def __str__(self):
        return self.name


class DailyMealStatus(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.BooleanField(default=True)

    class Meta:
        unique_together = ("student", "date")

    def __str__(self):
        return f"{self.student.name} - {self.date} {'ON' if self.status else 'OFF'}"


class MonthlyMealType(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    month = models.DateField()
    meal_type = models.IntegerField(choices=[(1, "Type 1"), (2, "Type 2")])

    class Meta:
        unique_together = ("student", "month")

    def __str__(self):
        return f"{self.student.name} - {self.month.strftime('%B %Y')} - Type {self.meal_type}"


class MonthlyMealSummary(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    total_days_meal_consumed = models.IntegerField(default=0)
    actual_meal_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    staff_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    #ongoing_meal_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    #total_meal_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def total_meal_cost(self):
        return self.actual_meal_cost + self.staff_cost + self.other_costs
    
    def __str__(self):
        return f"{self.student.name} Meal Summary"


# class ManagerView(models.Model):
#     student = models.OneToOneField(Student, on_delete=models.CASCADE)
#     student_meal_status = models.BooleanField(default=True)
#     meal_type = models.IntegerField()
