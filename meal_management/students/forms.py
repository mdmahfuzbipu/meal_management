from django import forms
from .models import MealType

class MealTypeChangeForm(forms.Form):
    meal_type = forms.ModelChoiceField(queryset=MealType.objects.all(), widget=forms.RadioSelect)
    