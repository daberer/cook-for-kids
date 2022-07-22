
import calendar
import datetime
from .models import Kid, Holiday
import random

def evaluate_result(result: dict, all_days: dict, leftover_dishes: list) -> int:
    score = 0



    #check doubles per week
    week = []
    for day in result:
        week.append(result[day])
        if day.weekday == 5:
            doubles = len(week) - len(list(set(week)))
            score += doubles * 5
            week = []
            

    
    #leftovers
    if max(leftover_dishes) > 1:
        score += 10


    # sequences
    li = list(result.values())
    for i, l in enumerate(li):
        if i == 0:
            continue
        
        if l:
            if i > 3:
                if li[i-4] == l :
                    score += 1
            if i > 2:
                if li[i-3] == l:
                    score += 5
            if i > 1:
                if li[i-2] == l:
                    score += 10
            if i > 0:
                if li[i-1] == l:
                    score += 50
    return score
            


    print('hey')

def add_or_subtract_dish(c_dict: dict, c_key: str, add=True) -> dict:
    """
    function to reduce monthly_dishes by one.

    c_dict : dict
    Dictionary of kids and the monthly dishes still to cook this month

    c_key : str
    Name of one kid which acts as key of c_dict dictionary
    """
    if add:
        c_dict[c_key] += 1

    else:
        c_dict[c_key] -= 1
    return c_dict





def find_potential_cooks(day: datetime.date, current_block: dict, current_kids: dict) -> list:
    """
    Function to find potenial cooks for given day
    """
    kids_with_dishes_left_to_cook = [k for k, v in current_kids.items() if v > 0]
    kids_with_block_on_this_day = current_block[day]
    
    potenial_cooks = list(set(kids_with_dishes_left_to_cook) - set(kids_with_block_on_this_day))
    random.shuffle(potenial_cooks)
    return potenial_cooks


def calculate_month():
    # initializing the year and month
    year = 2022
    month = 8
    num_days = calendar.monthrange(year, month)[1]

    #get rid of saturdays and sundays
    all_days = [datetime.date(year, month, day) for day in range(1, num_days+1)]
    day_objects = [datetime.date(year, month, day) for day in range(1, num_days+1) if datetime.date(year, month, day).weekday() not in (5,6)]

    #get rid of holidays
    holidays_all = list(Holiday.objects.all())
    holidays_current = [ho.date for ho in holidays_all if (ho.date.year == year and ho.date.month == month)]
    #days_active = [day for day in day_objects if day not in (holidays_current)]
    result_dict = {day:'' for day in day_objects if day not in (holidays_current)}
    block_dict = {day:[] for day in day_objects if day not in (holidays_current)}

    #get Kids
    kids = Kid.objects.all()
    kids_dict = {k.name:k.monthly_dishes for k in kids}

    def go_cooking(first=None, second=None):
        for key in result_dict:
            if result_dict[key] == '':
                potenial_cooks = find_potential_cooks(key, block_dict, kids_dict)
                found = 0
                
                for cook in potenial_cooks:
                    if cook == first or cook == second:
                        continue
                    result_dict[key] = cook
                    add_or_subtract_dish(kids_dict, cook, add=False) #kid will cook -> -1 dishes

                    if key == list(result_dict.keys())[-1]:
                        return True

                    if go_cooking(first=cook, second=first):
                        found = 1
                        break

                if not found:
                    kid = result_dict[key]
                    if kid != '': #consider case that noone could be found
                        add_or_subtract_dish(kids_dict, kid, add=True) #kid will not cook today -> +1 dishes
                    result_dict[key] = ''
                    return False

                else: 
                    return True
    
    if not go_cooking():
        print('No solution possible')
        return
    else:
        print('success')
        
        # fill up month
        for day in all_days:
            if day not in result_dict.keys():
                result_dict[day] = None
        
        result_dict = dict(sorted(result_dict.items()))
        score = evaluate_result(result_dict, all_days, list(kids_dict.values()))

        if score > 0:
            return

         

        kids_dict = {k: v for k,v in kids_dict.items() if v != 0}
        return score, kids_dict, {key.strftime("%m/%d/%Y"): value for key, value in result_dict.items()}


    #TODO: take into account block days, choose lucky parents first and reduce their contingent before running the function (will lead to less results)

def additional_holidays(days):
    """
    Function that adds new holidays single or in bulk
    """
    month = 8
    year = 2022
    s_days = days.split('-')
    written_to_db = False


    def save_day(day_to_save):
        success = False
        holidays_all = list(Holiday.objects.all())
        holidays_datetimes = [days.date for days in holidays_all]
        if day_to_save.weekday() not in (5,6) and day_to_save not in holidays_datetimes:         
            new_holiday = Holiday(date=day_to_save, text=str(day_to_save))
            new_holiday.save()
            success = True
        return success


    try:       
        if len(s_days) > 1:
            days_list = list(range(int(s_days[0]), int(s_days[1])+1))
            for day in days_list:
                this_day = datetime.date(year, month, day)
                written_to_db = save_day(this_day)
                
                
        elif len(s_days) == 1:
            day = int(s_days[0])
            this_day = datetime.date(year, month, day)       
            written_to_db = save_day(this_day)
            

        else:
            return ('False input')           
            

    except Exception as e:
        return (f'Failure because of {e}')

    if written_to_db:
        return 'success'
    return 'Holiday(s) were already in database'
  


if __name__ == '__main__':
    calculate_month()
    
    