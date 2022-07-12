
import calendar
import datetime
from .models import Kid

def calculate_month():
    # initializing the year and month
    year = 2020
    month = 1
    # printing the calendar
    print(calendar.month(year, month))
    names = Kid.objects.all()
    print(names)
    


if __name__ == '__main__':
    calculate_month()
    
    