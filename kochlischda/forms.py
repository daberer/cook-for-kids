from django import forms
from .models import Kid
import datetime

now = datetime.datetime.now()
year = now.year
month = now.month
if month == 12:
    month = 1
else:
    month+= 1

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


class WaiverdaysForm(forms.Form):
    year = forms.ChoiceField(choices=years)
    month = forms.ChoiceField(choices=MONTHS, initial=str(month))
    kid = forms.ModelMultipleChoiceField(queryset=Kid.objects.all())
    dates = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'e.g.: 1, 10-15'}))
    dishes_this_month = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Number of meals to cook this month'}))
    wishdays = forms.BooleanField(required=False)
    
