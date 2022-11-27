
import calendar
import datetime
from .models import Kid, Holiday, Waiverday
import random

def evaluate_result(result: dict, all_days: dict, leftover_dishes: list) -> int:
    score = 0

    #leftovers
    if max(leftover_dishes) > 1:
        score += 10
    
    return score


    """ #check doubles per week
    week = []
    for day in result:
       week.append(result[day])
       if day.weekday == 5:
           doubles = len(week) - len(list(set(week)))
           score += doubles * 5
           week = []
            

    
    


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
             """




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



def find_potential_cooks(day: datetime.date, current_block: dict, current_kids: dict, first: str) -> list:
    """
    Function to find potenial cooks for given day
    """
    #TODO: get rid of current block variable
    kids_with_dishes_left_to_cook = [k for k, v in current_kids.items() if v > 0]

    #find kids with block today
    
    try:
        waiverday = Waiverday.objects.filter(date=day)[0]
        kids_with_block_on_this_day = [kid.name for kid in waiverday.kid.all()]
    except IndexError as e:
        waiverday = None
        kids_with_block_on_this_day = []
    
    
    
    potenial_cooks = list(set(kids_with_dishes_left_to_cook) - set(kids_with_block_on_this_day) - set([first]))
    random.shuffle(potenial_cooks)
    return potenial_cooks


def calculate_month(it=None):
    # initializing the year and month
    year = 2022
    month = 12
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
                potenial_cooks = find_potential_cooks(key, block_dict, kids_dict, first)
                found = 0
                
                for cook in potenial_cooks:
                    #if cook == first:# or cook == second:
                    #    continue
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
        print(f'try {it} - No solution possible')
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

def check_correctness(df):
    """
    Quick check if current dict has entries that are in conflict with the Waiverday table
    """
    try:
        di = df[2]
    except Exception:
        return
    for item in di.items():
        try:
            if item[1] == None:
                continue
            a = Waiverday.objects.get(date=datetime.datetime.strptime(item[0], '%m/%d/%Y'))
            kids = a.kid.all()
            k = Kid.objects.get(name=item[1])
            if k in kids:
                return True
        except Exception:
            pass
    return False

def optimise(dframe):
    print('optimising..')
    def swap(df, date1, date2):
        cf = df.copy(deep=True)
        swapkid = df.at[date1, df.keys()[0]]
        cf.at[date1, df.keys()[0]] = cf.at[date2, df.keys()[0]]
        cf.at[date2, df.keys()[0]] = swapkid
        return cf

    def rate(d, kid1, kid2):
        """
        finds max days between first and last occurence
        finds min rest days between meals
        """

        min_kid1 = d[d[d.keys()[0]] == kid1].index[0].date()
        max_kid1 = d[d[d.keys()[0]] == kid1].index[-1].date()

        max_days_kid1 = 0
        if min_kid1 != max_kid1:
           max_days_kid1 = (max_kid1 - min_kid1).days


        min_kid2 = d[d[d.keys()[0]] == kid2].index[0].date()
        max_kid2 = d[d[d.keys()[0]] == kid2].index[-1].date()

        max_days_kid2 = 0
        if min_kid2 != max_kid2:
           max_days_kid2 = (max_kid2 - min_kid2).days
        sum_max = max_days_kid1 + max_days_kid2
        kid1_min_rest_days = d[d[d.keys()[0]].eq(kid1)].groupby(d.keys()[0]).diff().index.to_series().diff().min().days
        kid1_mean_rest_days = d[d[d.keys()[0]].eq(kid1)].groupby(d.keys()[0]).diff().index.to_series().diff().mean().days
        kid2_min_rest_days = d[d[d.keys()[0]].eq(kid2)].groupby(d.keys()[0]).diff().index.to_series().diff().min().days
        kid2_mean_rest_days = d[d[d.keys()[0]].eq(kid2)].groupby(d.keys()[0]).diff().index.to_series().diff().mean().days

        return sum_max, kid1_min_rest_days, kid2_min_rest_days, kid1_mean_rest_days, kid2_mean_rest_days

    def run_loop(df):
        for i, row in df.iterrows():
            kid1 = df.at[i, df.keys()[0]]


            if not row[0]:
                continue
            r = i
            breakout = 0
            while i == r:
                breakout+=1
                if breakout == 100:
                    continue
                r = df.index[random.randint(0, len(df)-1)]
                kid2 = df.at[r, df.keys()[0]]
                if kid1 == kid2 or kid2 is None:
                    r = i
                    continue
                # check waiverdays 
                # Problem if Waiverday.object does not exist -> therefore try statements
                try:
                    waiverday1 = Waiverday.objects.get(date=i).kid.all()
                except Waiverday.DoesNotExist:
                    waiverday1 = []
                try:
                    waiverday2 = Waiverday.objects.get(date=r).kid.all()
                except Waiverday.DoesNotExist:
                    waiverday2 = []
                try:
                    if Kid.objects.get(name=kid2) in waiverday1 or Kid.objects.get(name=kid1) in waiverday2:
                        r = i
                except Exception as e:
                    print(f'error {e}, -kid1{kid1}, -kid2{kid2}')


            to_1, k1_1, k2_1, km1_1, km2_1 = rate(df, df.at[i, df.keys()[0]], df.at[r, df.keys()[0]])
            kf = swap(df, i, r)
            to_2, k1_2, k2_2, km1_2, km2_2 = rate(kf, df.at[i, df.keys()[0]], df.at[r, df.keys()[0]])
            if to_2 >= to_1 and k1_2 >= k1_1 and k2_2 >= k2_1 and km1_2 >= km1_1 and km2_2 >= km2_1:
                df = kf
        return df

    for i in range(50):
        dframe = run_loop(dframe)
    return dframe


def additional_holidays(days):
    """
    Function that adds new holidays single or in bulk
    """
    month = 12
    year = 2022
    s_days_array = days.split(',')
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
        for s_days in s_days_array:       
            if '-' in s_days:
                s_days = s_days.split('-')
                days_list = list(range(int(s_days[0]), int(s_days[1])+1))
                for day in days_list:
                    this_day = datetime.date(year, month, day)
                    written_to_db = save_day(this_day)
                    
                    
            else:
                day = int(s_days[0])
                this_day = datetime.date(year, month, day)       
                written_to_db = save_day(this_day)
                

                      
            

    except Exception as e:
        return (f'Failure because of {e}')

    if written_to_db:
        return 'success'
    return 'Holiday(s) were already in database'

def additional_waiverdays(days, wishdays=False, kid=None, dishes_this_month=None, month=None, year=None):
    """
    Function that adds new holidays single or in bulk
    """
    if not kid:
        return 'No kid specified'
    month = int(month)
    year = int(year)
    

    num_days = calendar.monthrange(year, month)[1]
    all_days = [day for day in range(1, num_days+1)]

    days = days.strip()
    s_days_array = days.split(',')
    written_to_db = False


    def save_day(day_to_save, kid):
        success = False
        waiverdays_all = list(Waiverday.objects.all())
        waiverdays_datetimes = [days.date for days in waiverdays_all]
        if day_to_save.weekday() not in (5,6):
            if day_to_save in waiverdays_datetimes:
                old_waiverday = Waiverday.objects.filter(date=day_to_save)[0]
                old_waiverday.kid.add(kid)
                success = True
            else:
                new_waiverday = Waiverday(date=day_to_save)
                new_waiverday.save()
                new_waiverday.kid.add(kid)
                success = True
        return success

    try:
        for s_days in s_days_array:       
            if '-' in s_days:
                s_days = s_days.split('-')  
                days_list = list(range(int(s_days[0]), int(s_days[1])+1))
                if wishdays: #Todo: fix this
                    days_list = list(set(all_days) - set(days_list))


                for day in days_list: 
                    this_day = datetime.date(year, month, day)
                    written_to_db = save_day(this_day, kid)
                    
                    
            else:
                #Todo: add wishday feature here
                day = int(s_days)
                this_day = datetime.date(year, month, day)       
                written_to_db = save_day(this_day, kid)


    except Exception as e:
        return (f'Failure because of {e}')

    if written_to_db:
        return 'success'
    return 'Waiverday(s) already in database'


def get_list_of_kids():
    return [kid for kid in Kid.objects.all()]




         
            


  


if __name__ == '__main__':
    calculate_month()
    
    