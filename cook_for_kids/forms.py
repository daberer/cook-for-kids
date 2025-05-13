from django import forms
from .models import Kid, GlobalSettings

# These can stay at module level since they don't depend on database values
MONTHS = (
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

ONETWOTHREE = (
    (1, 'ONE'),
    (2, 'TWO'),
    (3, 'THREE'),
)


class WaiverdaysForm(forms.Form):
    # These will be properly initialized in __init__
    year = forms.ChoiceField()  
    month = forms.ChoiceField(choices=MONTHS)
    kid = forms.ModelChoiceField(
        queryset=Kid.objects.none(),
        widget=forms.Select(attrs={'size': 10, 'id': 'id_kid'})
    )
    dish = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g.: Dinkelwurstnudeln, vegetarische Laibchen, Hühnerfleisch, Rohkost + Schokolade und Vanille Pudding',
            'id': 'id_dish'
        })
    )
    dates = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'Sperrtage: e.g., 1, 10-15, 18-19'})
    )
    dishes_this_month = forms.IntegerField(
        required=False, 
        widget=forms.TextInput(attrs={
            'placeholder': 'Number of meals to cook this month',
            'id': 'id_dishes_this_month'
        })
    )
    wishdays = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get fresh settings from the database
        settings = GlobalSettings.get_current()
        current_year = settings.current_year = settings.year

        # Generate a more flexible range of years (5 years before and after current year)
        year_range = 5
        years = [(str(y), str(y)) for y in range(current_year-year_range, current_year+year_range+1)]

        # Update the year field with fresh choices and current year as initial
        self.fields['year'].choices = years

        # Set initial year and month if not already provided
        if 'initial' not in kwargs or 'year' not in kwargs.get('initial', {}):
            self.initial['year'] = str(current_year)

        if 'initial' not in kwargs or 'month' not in kwargs.get('initial', {}):
            self.initial['month'] = str(settings.month)

        # Update kid queryset
        try:
            kids = Kid.objects.all()
            self.fields['kid'].queryset = kids
            self.fields['kid'].widget.attrs['size'] = len(kids) + 1
        except Exception as e:
            # Handle database errors gracefully
            pass


class DataframeChoice(forms.Form):
    df_number = forms.ChoiceField(choices=ONETWOTHREE, initial='1')

class AdditionalHolidaysForm(forms.Form):
    dates = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'e.g.: 1, 10-15'}))
