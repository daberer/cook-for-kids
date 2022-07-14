
import calendar
import datetime
from .models import Kid, Holiday


def subtract_dish(c_dict, c_key):
    """
    function to reduce monthly_dishes by one.

    c_dict : dict
    Dictionary of kids and the monthly dishes still to cook this month

    c_key : str
    Name of one kid which acts as key of c_dict dictionary
    """
    assert type(c_dict) == dict
    assert type(c_key) == str
    if c_dict[c_key] == 1:
        del c_dict[c_key]
    else:
        c_dict[c_key] -= 1
    return c_dict


def calculate_month():
    # initializing the year and month
    year = 2022
    month = 7
    # printing the calendar
    num_days = calendar.monthrange(year, month)[1]

    #get rid of saturdays and sundays
    day_objects = [datetime.date(year, month, day) for day in range(1, num_days+1) if datetime.date(year, month, day).weekday() not in (5,6)]

    #get rid of holidays
    holidays_all = list(Holiday.objects.all())
    holidays_current = [ho.date for ho in holidays_all if (ho.date.year == year and ho.date.month == month)]
    days_active = [day for day in day_objects if day not in (holidays_current)]
    result_dict = {day:'' for day in day_objects if day not in (holidays_current)}

    #get Kids
    kids = Kid.objects.all()
    kids_dict = {k.name:k.monthly_dishes for k in kids}

    def go_cooking():
        for d in days_active:
            pass
    #TODO: write recursive and randomised function that assigns the days to the kids, take into account block days, write a function that ranks the outcome of the assignment, then run 1000s of times
  


if __name__ == '__main__':
    calculate_month()
    
    