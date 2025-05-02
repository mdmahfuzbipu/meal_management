from django.contrib import admin

from .models import Student, MonthlyMealSummary, DailyMealStatus, MonthlyMealType

# Register your models here.

admin.site.register(Student)
admin.site.register(MonthlyMealSummary)
admin.site.register(DailyMealStatus)
admin.site.register(MonthlyMealType)
