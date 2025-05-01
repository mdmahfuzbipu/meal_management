from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Create your models here.
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    room = models.IntegerField()
    name = models.CharField(max_length=50)
    student_id = models.CharField(max_length=12, unique=True)
    department = models.CharField(max_length=50)
    floor = models.CharField(max_length=15)
    batch = models.CharField(max_length=10)
    meal_type = models.IntegerField(choices=[(1, 'Type 1'), (2, 'Type 2')])
    ongoing_meal_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_meal_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return self.name


class DailyMealStatus(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student.name} - {self.date} {"ON" if self.status else "OFF"}"

class MealSummary(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    total_days_meal_consumed = models.IntegerField(default=0)
    only_meal_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    staff_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_meal_cost = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    
    def __str__(self):
        return f"{self.student.name} Meal Summary"


class MealInfo(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    meal_status = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.student.name} Meal Info"
    

# class ManagerView(models.Model):
#     student = models.OneToOneField(Student, on_delete=models.CASCADE)
#     student_meal_status = models.BooleanField(default=True)
#     meal_type = models.IntegerField()