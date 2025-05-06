
import calendar
import datetime
from .models import Kid, Holiday, Waiverday, Dish
import random
from cook_for_kids.globals import Setup
import itertools

def evaluate_result(result: dict, all_days: dict, leftover_dishes: list) -> int:
    score = 0

    # leftovers
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
    # TODO: get rid of current block variable
    kids_with_dishes_left_to_cook = [
        k for k, v in current_kids.items() if v > 0]

    # find kids with block today

    try:
        waiverday = Waiverday.objects.filter(date=day)[0]
        kids_with_block_on_this_day = [kid.name for kid in waiverday.kid.all()]
    except IndexError as e:
        waiverday = None
        kids_with_block_on_this_day = []

    potenial_cooks = list(set(kids_with_dishes_left_to_cook) -
                          set(kids_with_block_on_this_day) - set([first]))
    random.shuffle(potenial_cooks)
    return potenial_cooks


def num_days_in_month(year, month):
    return calendar.monthrange(year, month)[1]


def get_cooking_schedule(year, month, num_days):
    """
    Generate cooking schedule data for a given month, excluding weekends and holidays.

    Parameters:
    - year (int): The year
    - month (int): The month (1-12)
    - num_days (int): Number of days in the month

    Returns:
    - dict: A tuple containing:
        - result_dict: Dictionary with available cooking days as keys and empty strings as values
        - block_dict: Dictionary with available cooking days as keys and empty lists as values
        - kids_dict: Dictionary with kid names as keys and their monthly dishes as values
        - kochdienste: Total number of cooking duties assigned to all kids
        - kochtage: Number of available cooking days in the month
    """

    # Get all days in the month and filter out weekends (Saturday=5, Sunday=6)
    all_days = [datetime.date(year, month, day) for day in range(1, num_days+1)]
    day_objects = [day for day in all_days if day.weekday() not in (5, 6)]

    # Filter out holidays
    holidays_all = list(Holiday.objects.all())
    holidays_current = [ho.date for ho in holidays_all if (
        ho.date.year == year and ho.date.month == month)]

    # Create dictionaries for available cooking days
    result_dict = {day: '' for day in day_objects if day not in holidays_current}
    block_dict = {day: [] for day in day_objects if day not in holidays_current}

    # Get kids and their monthly cooking duties
    kids = Kid.objects.all()
    kids_dict = {k.name: k.monthly_dishes for k in kids}

    # Calculate totals for cooking duties and available days
    kochdienste = sum(kids_dict.values())
    kochtage = len(result_dict)

    return {
        'result_dict': result_dict,
        'block_dict': block_dict,
        'kids_dict': kids_dict,
        'kochdienste': kochdienste,
        'kochtage': kochtage,
        'all_days': all_days
    }


def calculate_month(it=1, test=False):
    # initializing the year and month
    year = Setup.year
    month = Setup.month
    if test:
        year, month = 2025, 5

    num_days = num_days_in_month(year, month) 
        
    cooking_data = get_cooking_schedule(year, month, num_days)

    kochdienste = cooking_data['kochdienste']
    kochtage = cooking_data['kochtage']
    block_dict = cooking_data['block_dict']
    all_days = cooking_data['all_days']
    

    
    if  kochdienste < kochtage :
        print(f'Not enough Kochdienste ({kochdienste}), for {kochtage} Kochtage this month.')
        return

    def go_cooking(first=None, second=None):
        for key in result_dict:
            if result_dict[key] == '':
                potenial_cooks = find_potential_cooks(
                    key, block_dict, kids_dict, first)
                found = 0

                for cook in potenial_cooks:
                    # if cook == first:# or cook == second:
                    #    continue
                    result_dict[key] = cook
                    # kid will cook -> -1 dishes
                    add_or_subtract_dish(kids_dict, cook, add=False)

                    if key == list(result_dict.keys())[-1]:
                        return True

                    if go_cooking(first=cook, second=first):
                        found = 1
                        break

                if not found:
                    kid = result_dict[key]
                    if kid != '':  # consider case that noone could be found
                        # kid will not cook today -> +1 dishes
                        add_or_subtract_dish(kids_dict, kid, add=True)
                    result_dict[key] = ''
                    return False

                else:
                    return True

    if not go_cooking():
        print(f'try {it} - No solution possible')
        return
    else:
        max_luck = 0
        lucky_kids = []
        lucky = []
        for kid, luck in kids_dict.items():
            if luck > 0:
                if luck > max_luck:
                    max_luck = luck
                lucky.append(f'kid:{kid}, luck:{luck}')
                lucky_kids.append(kid)
                
        print(f'success, luckies: {lucky}')
        
        # fill up month
        for day in all_days:
            if day not in result_dict.keys():
                result_dict[day] = None
        
        result_dict = dict(sorted(result_dict.items()))
        score = evaluate_result(result_dict, all_days, list(kids_dict.values()))

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

def check_correctness_df(df):
    """
    Quick check if current dataframe has entries that are in conflict with the Waiverday table
    """
    for i, row in df.iterrows():
        if row[0] == '':
            continue
        try:
            a = Waiverday.objects.get(date=(i))
        except Exception:
            continue
        k = Kid.objects.get(name=row[0])
        kids = a.kid.all()
        if k in kids:
            return (f'{row[0]} has a waiverday on {i}!')
    return 'All good.'

def optimise(dframe):
    print('optimising..')
    
    def swap(df, date1, date2):
        swapkid = df.at[date1, df.columns[0]]
        df.at[date1, df.columns[0]] = df.at[date2, df.columns[0]]
        df.at[date2, df.columns[0]] = swapkid
        return df

    def rate(d, kid1, kid2):
        kid1_dates = d[d[d.columns[0]] == kid1].index
        kid2_dates = d[d[d.columns[0]] == kid2].index

        if kid1_dates.empty or kid2_dates.empty:
            return float('inf'), float('inf'), float('inf'), float('inf'), float('inf')

        min_kid1 = kid1_dates[0].date()
        max_kid1 = kid1_dates[-1].date()
        min_kid2 = kid2_dates[0].date()
        max_kid2 = kid2_dates[-1].date()

        max_days_kid1 = (max_kid1 - min_kid1).days if min_kid1 != max_kid1 else 0
        max_days_kid2 = (max_kid2 - min_kid2).days if min_kid2 != max_kid2 else 0
        sum_max = max_days_kid1 + max_days_kid2

        kid1_diff = kid1_dates.to_series().diff().dt.days
        kid1_min_rest_days = kid1_diff.min()
        kid1_mean_rest_days = kid1_diff.mean()
        
        kid2_diff = kid2_dates.to_series().diff().dt.days
        kid2_min_rest_days = kid2_diff.min()
        kid2_mean_rest_days = kid2_diff.mean()

        return sum_max, kid1_min_rest_days, kid2_min_rest_days, kid1_mean_rest_days, kid2_mean_rest_days

    def run_loop(df):
        for i in df.index:
            kid1 = df.at[i, df.columns[0]]

            if not kid1:
                continue

            for _ in range(100):
                r = df.index[random.randint(0, len(df) - 1)]
                kid2 = df.at[r, df.columns[0]]
                if kid1 != kid2 and kid2:
                    try:
                        waiverday1 = Waiverday.objects.get(date=i).kid.all()
                    except Waiverday.DoesNotExist:
                        waiverday1 = []
                    try:
                        waiverday2 = Waiverday.objects.get(date=r).kid.all()
                    except Waiverday.DoesNotExist:
                        waiverday2 = []

                    if (Kid.objects.get(name=kid2) not in waiverday1 and
                        Kid.objects.get(name=kid1) not in waiverday2):
                        break
            else:
                continue

            to_1, k1_1, k2_1, km1_1, km2_1 = rate(df, kid1, kid2)
            kf = swap(df.copy(), i, r)
            to_2, k1_2, k2_2, km1_2, km2_2 = rate(kf, kid1, kid2)
            if to_2 >= to_1 and k1_2 >= k1_1 and k2_2 >= k2_1 and km1_2 >= km1_1 and km2_2 >= km2_1:
                df = kf
        return df

    for _ in range(50):
        dframe = run_loop(dframe)
    return dframe


def additional_holidays(days):
    """
    Function that adds new holidays single or in bulk
    """
    month = Setup.month
    year = Setup.year
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
                day = int(s_days)
                this_day = datetime.date(year, month, day)       
                written_to_db = save_day(this_day)    
            

    except Exception as e:
        return (f'Failure because of {e}')

    if written_to_db:
        return 'success'
    return 'Holiday(s) were already in database'


def additional_waiverdays(days, wishdays=False, kid=None, dishes_this_month=None, month=None, year=None, dish=None):
    """
    Function that adds new holidays single or in bulk
    """
    res = ''
    if not kid:
        return 'No kid specified'

    if dishes_this_month is not None:
        current_kid = Kid.objects.filter(name=kid).first()
        current_kid.monthly_dishes = dishes_this_month
        current_kid.save()
        res += 'kid updated, '

    dish_object = Dish.objects.filter(cook=kid).first()
    if dish_object:
        dish_object.dish_name = dish
        dish_object.save()
    
    else:
        new_dish = Dish(dish_name=dish, cook=kid)            
        new_dish.save()
    res+='dish updated'

    
    month = int(month)
    year = int(year)

    if days == '':
        Waiverday.objects.filter(
            date__year=year,
            date__month=month,
            kid=kid
        ).delete()
        return f'Waiverdays for {kid} deleted'


    num_days = calendar.monthrange(year, month)[1]
    all_days = [day for day in range(1, num_days+1)]

    days = days.strip()
    s_days_array = days.split(',')

    
    def entry_split(day):
        if '-' in day:
            sp = day.split('-')
            return list(range(int(sp[0]), int(sp[1])+1))
        return [int(day)]

    mylists = [entry_split(x) for x in s_days_array]
    flat_list = list(itertools.chain(*mylists))
    if wishdays:
        flat_list = list(set(all_days) - set(flat_list))

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
        for day in flat_list:       
            this_day = datetime.date(year, month, day)
            written_to_db = save_day(this_day, kid)             


    except Exception as e:
        return (f'Failure because of {e}')

    if written_to_db:
        return 'success'
    return 'Waiverday(s) already in database'


def get_list_of_kids():
    return [kid for kid in Kid.objects.all()]


def get_kid_dates_dict(selected_year, selected_month):
    kid_dates_dict = {}
    for kid in Kid.objects.all():
        # Get waiver days for this kid in the selected month
        waiver_days = []
        for waiverday in kid.waiverdaykids.filter(
            date__year=selected_year, 
            date__month=selected_month
        ).order_by('date'):
            waiver_days.append(waiverday.date.day)

        # Format the dates as a string (e.g., "1, 5, 10-15")
        formatted_dates = format_date_ranges(waiver_days)
        kid_dates_dict[str(kid.id)] = formatted_dates
    return kid_dates_dict


def format_date_ranges(days):
    """Format a list of days into a string with ranges.
    Example: [1, 2, 3, 5, 8, 9, 10] becomes "1-3, 5, 8-10"
    """
    if not days:
        return ""

    days.sort()
    ranges = []
    start = days[0]
    end = days[0]

    for i in range(1, len(days)):
        if days[i] == end + 1:
            end = days[i]
        else:
            if start == end:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{end}")
            start = end = days[i]

    # Add the last range
    if start == end:
        ranges.append(str(start))
    else:
        ranges.append(f"{start}-{end}")

    return ", ".join(ranges)

if __name__ == '__main__':
    calculate_month()
    
    