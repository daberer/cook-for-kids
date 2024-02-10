from django import forms
from .models import Kid
import datetime
from .globals import Setup

year = Setup.year
month = Setup.month
frame = 1


years = (
(year, year),
(year+1, year+1)
)

MONTHS= (
('1', 'Jan'),
('2', 'Feb'),
('3', 'Mar'),
('4', 'Apr'),
('5', 'May'),
('6', 'Jun'),
('7', 'Jul'),
('8', 'Aug'),
('9', 'Sep'),
('10', 'Oct'),
('11', 'Nov'),
('12', 'Dec'),
)

ONETWOTHREE=((1, 'ONE'),
            (2, 'TWO'),
            (3, 'THREE'),)


class WaiverdaysForm(forms.Form):
    year = forms.ChoiceField(choices=years)
    month = forms.ChoiceField(choices=MONTHS, initial=str(month))
    kid = forms.ModelMultipleChoiceField(queryset=Kid.objects.all())
    dish = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'e.g.: Dinkelwurstnudeln, vegetarische Laibchen, Hühnerfleisch, Rohkost + Schokolade und Vanille Pudding'}))
    dates = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'e.g.: 1, 10-15'}))
    dishes_this_month = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Number of meals to cook this month'}))
    wishdays = forms.BooleanField(required=False)


class DataframeChoice(forms.Form):
    df_number = forms.ChoiceField(choices=ONETWOTHREE, initial=str(frame))
    
