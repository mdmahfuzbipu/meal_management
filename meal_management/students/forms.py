from django import forms

class MealTypeChangeForm(forms.Form):
    MEAL_TYPE_CHOICES = [(1, 'Beef'), (2, 'Fish')]
    meal_type = forms.ChoiceField(choices=MEAL_TYPE_CHOICES, widget=forms.RadioSelect)