from django import forms

class MealTypeChangeForm(forms.Form):
    MEAL_TYPE_CHOICES = [(1, 'Type 1'), (2, 'Type 2')]
    meal_type = forms.ChoiceField(choices=MEAL_TYPE_CHOICES, widget=forms.RadioSelect)