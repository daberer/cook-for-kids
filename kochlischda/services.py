
import calendar
import datetime
from .models import Kid

def calculate_month():
    # initializing the year and month
    year = 2020
    month = 1
    # printing the calendar
    print(calendar.month(year, month))
    


if __name__ == '__main__':
    calculate_month()
    #kids_list = ['Antonia', 'Balthasar', 'Caroline', 'Dodo']
    #menu_list = ['Algenbuger', 'Braten', 'Cornflakes', 'Dattelmuffins']
    
    a = Kid(name='Antonia', exempt=True, gender='girl', monthly_dishes_number=0)
    b = Kid(name='Balthasar', exempt=False, gender='boy')

    print(a)
    print(b)
    
    