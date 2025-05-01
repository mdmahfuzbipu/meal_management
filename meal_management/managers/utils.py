from students.models import MealInfo
from .models import MealCount
from django.utils import timezone

def generate_meal_count():
    type1_count = MealInfo.objects.filter(meal_status=True, student__meal_type=1)
    type2_count = MealInfo.objects.filter(meal_status=True, student__meal_type=2)
    
    MealCount.objects.create(
        date=timezone.now().date(),
        meal_type1_total=type1_count,
        meal_type2_total=type2_count
    )