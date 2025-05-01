from django.db import models

# Create your models here.
class MealCount(models.Model):
    date = models.DateField(auto_now_add=True)
    meal_type1_total = models.IntegerField()
    meal_type2_total = models.IntegerField()
    
    
    def total_meals_on(self):
        return self.meal_type1_total + self.meal_type2_toal
    
    
    def __str__(self):
        return f"Meal Count on {self.date}"