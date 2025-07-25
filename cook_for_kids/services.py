import calendar
import datetime
from .models import Kid, Holiday, Waiverday, Dish, GlobalSettings
import random, os
import itertools
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import textwrap
from django.db.models import Q
from functools import reduce
import operator
from typing import Optional
import pandas as pd
from dataclasses import dataclass
from cook_for_kids.settings import PDF_DIR


def evaluate_result(result: dict, all_days: dict,
                    leftover_dishes: list) -> int:
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


def find_potential_cooks(day: datetime.date, current_block: dict,
                         current_kids: dict, first: str) -> list:
    """
    Function to find potenial cooks for given day
    """
    # TODO: get rid of current block variable
    kids_with_dishes_left_to_cook = [
        k for k, v in current_kids.items() if v > 0
    ]

    # find kids with block today

    try:
        waiverday = Waiverday.objects.filter(date=day)[0]
        kids_with_block_on_this_day = [kid.name for kid in waiverday.kid.all()]
    except IndexError as e:
        waiverday = None
        kids_with_block_on_this_day = []

    potenial_cooks = list(
        set(kids_with_dishes_left_to_cook) - set(kids_with_block_on_this_day) -
        set([first]))
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
    all_days = [
        datetime.date(year, month, day) for day in range(1, num_days + 1)
    ]
    day_objects = [day for day in all_days if day.weekday() not in (5, 6)]

    # Filter out holidays
    holidays_all = list(Holiday.objects.all())
    holidays_current = [
        ho.date for ho in holidays_all
        if (ho.date.year == year and ho.date.month == month)
    ]

    # Create dictionaries for available cooking days
    result_dict = {
        day: ''
        for day in day_objects if day not in holidays_current
    }
    block_dict = {
        day: []
        for day in day_objects if day not in holidays_current
    }

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
    settings = GlobalSettings.get_current()
    year = settings.year
    month = settings.month
    if test:
        year, month = 2025, 5

    num_days = num_days_in_month(year, month)

    cooking_data = get_cooking_schedule(year, month, num_days)

    kochdienste = cooking_data['kochdienste']
    kochtage = cooking_data['kochtage']
    block_dict = cooking_data['block_dict']
    all_days = cooking_data['all_days']
    result_dict = cooking_data['result_dict']
    kids_dict = cooking_data['kids_dict']

    if kochdienste < kochtage:
        print(
            f'Not enough Kochdienste ({kochdienste}), for {kochtage} Kochtage this month.'
        )
        return

    def go_cooking(first=None, second=None):
        for key in result_dict:
            if result_dict[key] == '':
                potenial_cooks = find_potential_cooks(key, block_dict,
                                                      kids_dict, first)
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
        print(f'try {it}: No solution found')
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

        print(f'try {it}: Success! luckies: {lucky}')

        # fill up month
        for day in all_days:
            if day not in result_dict.keys():
                result_dict[day] = None

        result_dict = dict(sorted(result_dict.items()))
        score = evaluate_result(result_dict, all_days,
                                list(kids_dict.values()))

        kids_dict = {k: v for k, v in kids_dict.items() if v != 0}
        return score, kids_dict, {
            key.strftime("%m/%d/%Y"): value
            for key, value in result_dict.items()
        }

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
            a = Waiverday.objects.get(
                date=datetime.datetime.strptime(item[0], '%m/%d/%Y'))
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
            return (f'Conflicts: {row[0]} has a waiverday on {i}!')
    return 'Conflicts: All good.'


@dataclass
class OptimizationMetrics:
    """Metrics used to evaluate schedule quality."""
    total_span_days: float
    kid1_min_rest_days: float
    kid2_min_rest_days: float
    kid1_avg_rest_days: float
    kid2_avg_rest_days: float

class ScheduleOptimizer:
    """Optimizes kid schedules by swapping assignments to improve rest day distribution."""

    def __init__(self, max_swap_attempts: int = 100, optimization_rounds: int = 100):
        self.max_swap_attempts = max_swap_attempts
        self.optimization_rounds = optimization_rounds
        self._waiver_cache = {}

    def optimize_schedule(self, schedule_df: pd.DataFrame, kid_column: str = None) -> pd.DataFrame:
        """
        Optimize a schedule by swapping kid assignments to improve rest day distribution.

        Args:
            schedule_df: DataFrame with dates as index and kid assignments
            kid_column: Name of column containing kid assignments (defaults to first column)

        Returns:
            Optimized DataFrame with improved rest day distribution
        """
        if schedule_df.empty:
            return schedule_df

        kid_column = kid_column or schedule_df.columns[0]
        optimized_schedule = schedule_df.copy()

        print(f"Starting optimization for {len(schedule_df)} schedule entries...")

        for round_num in range(self.optimization_rounds):
            optimized_schedule = self._run_optimization_round(optimized_schedule, kid_column)

        return optimized_schedule

    def _run_optimization_round(self, schedule_df: pd.DataFrame, kid_column: str) -> pd.DataFrame:
        """Run a single round of optimization attempts."""
        current_schedule = schedule_df.copy()

        for date_idx in schedule_df.index:
            current_kid = schedule_df.at[date_idx, kid_column]

            if pd.isna(current_kid) or not current_kid:
                continue

            swap_candidate = self._find_valid_swap_candidate(
                schedule_df, date_idx, current_kid, kid_column
            )

            if swap_candidate is None:
                continue

            if self._should_perform_swap(current_schedule, date_idx, swap_candidate, kid_column):
                current_schedule = self._swap_assignments(
                    current_schedule, date_idx, swap_candidate, kid_column
                )

        return current_schedule

    def _find_valid_swap_candidate(self, schedule_df: pd.DataFrame, 
                                 current_date_idx, current_kid: str, 
                                 kid_column: str) -> Optional:
        """Find a valid date to swap with, considering waiver constraints."""
        for _ in range(self.max_swap_attempts):
            candidate_idx = random.choice(schedule_df.index)
            candidate_kid = schedule_df.at[candidate_idx, kid_column]

            if (candidate_kid and 
                candidate_kid != current_kid and 
                self._is_swap_allowed(current_date_idx, candidate_idx, current_kid, candidate_kid)):
                return candidate_idx

        return None

    def _is_swap_allowed(self, date1, date2, kid1: str, kid2: str) -> bool:
        """Check if swap is allowed based on waiver constraints."""
        try:
            # Cache waiver data to avoid repeated database queries
            waivers_date1 = self._get_waivers_for_date(date1)
            waivers_date2 = self._get_waivers_for_date(date2)

            # Check if kids can work on swapped dates
            kid1_obj = self._get_kid_object(kid1)
            kid2_obj = self._get_kid_object(kid2)

            return (kid2_obj not in waivers_date1 and 
                    kid1_obj not in waivers_date2)

        except Exception:
            # If we can't verify constraints, don't allow the swap
            return False

    def _should_perform_swap(self, schedule_df: pd.DataFrame, date1, date2, kid_column: str) -> bool:
        """Determine if a swap would improve the schedule quality."""
        kid1 = schedule_df.at[date1, kid_column]
        kid2 = schedule_df.at[date2, kid_column]

        current_metrics = self._calculate_metrics(schedule_df, kid1, kid2, kid_column)

        # Create temporary swapped schedule
        temp_schedule = self._swap_assignments(schedule_df.copy(), date1, date2, kid_column)
        swapped_metrics = self._calculate_metrics(temp_schedule, kid1, kid2, kid_column)

        return self._is_improvement(current_metrics, swapped_metrics)

    def _calculate_metrics(self, schedule_df: pd.DataFrame, kid1: str, kid2: str, 
                          kid_column: str) -> OptimizationMetrics:
        """Calculate optimization metrics for two kids."""
        kid1_dates = schedule_df[schedule_df[kid_column] == kid1].index
        kid2_dates = schedule_df[schedule_df[kid_column] == kid2].index

        if kid1_dates.empty or kid2_dates.empty:
            return OptimizationMetrics(
                float('inf'), float('inf'), float('inf'), float('inf'), float('inf')
            )

        # Calculate date spans
        kid1_span = (kid1_dates[-1].date() - kid1_dates[0].date()).days
        kid2_span = (kid2_dates[-1].date() - kid2_dates[0].date()).days
        total_span = kid1_span + kid2_span

        # Calculate rest day statistics
        kid1_rest_days = pd.Series(kid1_dates).diff().dt.days.dropna()
        kid2_rest_days = pd.Series(kid2_dates).diff().dt.days.dropna()

        return OptimizationMetrics(
            total_span_days=total_span,
            kid1_min_rest_days=kid1_rest_days.min() if not kid1_rest_days.empty else float('inf'),
            kid2_min_rest_days=kid2_rest_days.min() if not kid2_rest_days.empty else float('inf'),
            kid1_avg_rest_days=kid1_rest_days.mean() if not kid1_rest_days.empty else float('inf'),
            kid2_avg_rest_days=kid2_rest_days.mean() if not kid2_rest_days.empty else float('inf')
        )

    def _is_improvement(self, current: OptimizationMetrics, proposed: OptimizationMetrics) -> bool:
        """Check if proposed metrics represent an improvement."""
        return (proposed.total_span_days >= current.total_span_days and
                proposed.kid1_min_rest_days >= current.kid1_min_rest_days and
                proposed.kid2_min_rest_days >= current.kid2_min_rest_days and
                proposed.kid1_avg_rest_days >= current.kid1_avg_rest_days and
                proposed.kid2_avg_rest_days >= current.kid2_avg_rest_days)

    def _swap_assignments(self, schedule_df: pd.DataFrame, date1, date2, kid_column: str) -> pd.DataFrame:
        """Swap kid assignments between two dates."""
        schedule_df.at[date1, kid_column], schedule_df.at[date2, kid_column] = \
            schedule_df.at[date2, kid_column], schedule_df.at[date1, kid_column]
        return schedule_df

    def _get_waivers_for_date(self, date):
        """Get waiver information for a date (with caching)."""
        if date not in self._waiver_cache:
            try:
                from cook_for_kids.models import Waiverday  # Import where needed
                self._waiver_cache[date] = Waiverday.objects.get(date=date).kid.all()
            except Waiverday.DoesNotExist:
                self._waiver_cache[date] = []
        return self._waiver_cache[date]

    def _get_kid_object(self, kid_name: str):
        """Get kid object by name (could also be cached)."""
        from cook_for_kids.models import Kid  # Import where needed
        return Kid.objects.get(name=kid_name)

# Usage
def optimize_schedule(schedule_dataframe: pd.DataFrame) -> pd.DataFrame:
    """Public interface for schedule optimization."""
    optimizer = ScheduleOptimizer(max_swap_attempts=100, optimization_rounds=50)
    return optimizer.optimize_schedule(schedule_dataframe)


def add_or_subtract_holidays(days):
    """
    Function that adds or subtracts holidays single or in bulk based on set comparison
    """
    settings = GlobalSettings.get_current()
    year = settings.year
    month = settings.month

    # Parse the input days into a flat list
    flat_days = parse_day_ranges(days)

    # Get the current holidays for this month from the database
    current_monthly_holidays_in_db = get_holidays_this_month(year, month)
    flat_dates_in_db = []
    if not current_monthly_holidays_in_db == '':
        flat_dates_in_db = parse_day_ranges(current_monthly_holidays_in_db)

    # Set comparisons to find which days to add and which to remove
    days_to_add = set(flat_days) - set(flat_dates_in_db)
    days_to_remove = set(flat_dates_in_db) - set(flat_days)

    added_count = 0
    removed_count = 0

    # Add new holidays
    for day in days_to_add:
        this_day = datetime.date(year, month, day)
        # Skip weekends (5=Saturday, 6=Sunday)
        if this_day.weekday() not in (5, 6):
            try:
                # Check if holiday already exists
                if not Holiday.objects.filter(date=this_day).exists():
                    new_holiday = Holiday(date=this_day, text=str(this_day))
                    new_holiday.save()
                    added_count += 1
            except Exception as e:
                return f'Failure while adding holiday {this_day}: {e}'

    # Remove holidays that are no longer needed
    for day in days_to_remove:
        this_day = datetime.date(year, month, day)
        try:
            holidays_to_delete = Holiday.objects.filter(date=this_day)
            delete_count = holidays_to_delete.count()
            holidays_to_delete.delete()
            removed_count += delete_count
        except Exception as e:
            return f'Failure while removing holiday {this_day}: {e}'

    if added_count > 0 and removed_count > 0:
        return f'Success: Added {added_count} and removed {removed_count} holidays'
    elif added_count > 0:
        return f'Success: Added {added_count} holidays'
    elif removed_count > 0:
        return f'Success: Removed {removed_count} holidays'
    else:
        return 'No changes were needed to the holidays database'



def parse_day_ranges(day_string):
    """
    Converts a comma-separated string of day numbers and ranges to a flat list of integers.

    Example:
        >>> parse_day_ranges("1,3-5,7")
        [1, 3, 4, 5, 7]
    """
    day_string = day_string.strip()
    s_days_array = day_string.split(',')

    def entry_split(day):
        if '-' in day:
            sp = day.split('-')
            return list(range(int(sp[0]), int(sp[1]) + 1))
        return [int(day)]

    mylists = [entry_split(x) for x in s_days_array]
    return list(itertools.chain(*mylists))



def additional_waiverdays(days,
                          wishdays=False,
                          kid=None,
                          dishes_this_month=None,
                          month=None,
                          year=None,
                          dish=None):
    """
    Function that adds new holidays single or in bulk
    """
    res = ''
    if not kid:
        return 'No kid specified'

    if dishes_this_month is None:
        dishes_this_month = 0
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
    res += 'dish updated'

    month = int(month)
    year = int(year)

    waiverdays_this_month = Waiverday.objects.filter(date__year=year,
                                                     date__month=month,
                                                     kid=kid)
    if days == '':
        for waiverday in waiverdays_this_month:
            # Remove the specific kid
            waiverday.kid.remove(kid)

            # Check if any kids remain
            if waiverday.kid.exists():
                waiverday.save()
            else:
                waiverday.delete()
        return f'Waiverdays for {kid} deleted'

    num_days = calendar.monthrange(year, month)[1]
    all_days = [day for day in range(1, num_days + 1)]
    
    flat_list = parse_day_ranges(days)

    if wishdays:
        flat_list = list(set(all_days) - set(flat_list))

    flat_current_list = sorted([wai.date.day for wai in waiverdays_this_month])

    # Create sorted list of integers in flat_current_list but not in flat_list
    flat_delete_list = sorted(
        [x for x in flat_current_list if x not in flat_list])

    # Create sorted list of integers in flat_list but not in flat_current_list
    flat_list = sorted([x for x in flat_list if x not in flat_current_list])

    removed_from_db = False

    if len(flat_delete_list):
        waiverdays_to_remove_queryset = Waiverday.objects.filter(
            reduce(operator.or_, [Q(date__day=x) for x in flat_delete_list]),
            date__year=year,
            date__month=month,
            kid=kid)
        for waiverday in waiverdays_to_remove_queryset:
            # Remove the specific kid
            waiverday.kid.remove(kid)

            # Check if any kids remain
            if waiverday.kid.exists():
                waiverday.save()
            else:
                waiverday.delete()
            removed_from_db = True

    written_to_db = False

    def save_day(day_to_save, kid):
        success = False
        waiverdays_all = list(Waiverday.objects.all())
        waiverdays_datetimes = [days.date for days in waiverdays_all]
        if day_to_save.weekday() not in (5, 6):
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

    if written_to_db or removed_from_db:
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
                date__month=selected_month).order_by('date'):
            waiver_days.append(waiverday.date.day)

        # Format the dates as a string (e.g., "1, 5, 10-15")
        formatted_dates = format_date_ranges(waiver_days)
        kid_dates_dict[str(kid.id)] = formatted_dates
    return kid_dates_dict

def get_holidays_this_month(selected_year, selected_month):
    holidays_list = []
    for holiday in Holiday.objects.filter(date__year=selected_year, date__month=selected_month).order_by('date'):
        holidays_list.append(holiday.date.day)
    return format_date_ranges(holidays_list)



def validate_holiday_format(date_string):
    """
    Validates if the input string matches the expected format like "1,2,10-15,18-19"
    Returns (is_valid, error_message)
    """
    if not date_string.strip():
        return False, "Date input cannot be empty"

    # Split by comma and check each part
    parts = [part.strip() for part in date_string.split(',')]

    for part in parts:
        # Check if it's a single number
        if part.isdigit():
            continue
        # Check if it's a range (e.g., 10-15)
        elif '-' in part:
            range_parts = part.split('-')
            if len(range_parts) != 2 or not range_parts[0].isdigit() or not range_parts[1].isdigit():
                return False, f"Invalid range format: '{part}'. Expected format like '10-15'"
        else:
            return False, f"Invalid format: '{part}'. Expected single day (e.g., '5') or range (e.g., '10-15')"

    return True, ""


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


def create_styled_pdf(df):
    import pandas as pd
    settings = GlobalSettings.get_current()
    year = settings.year
    month = settings.month

    # Dictionary to convert month number to German month name
    month_dict = {
        1: 'Jänner',
        2: 'Februar',
        3: 'März',
        4: 'April',
        5: 'Mai',
        6: 'Juni',
        7: 'Juli',
        8: 'August',
        9: 'September',
        10: 'Oktober',
        11: 'November',
        12: 'Dezember'
    }

    # Get German month name
    month_name = month_dict.get(month, str(month))

    # Ensure directory exists
    pdf_path = f"{PDF_DIR}/{year}_{month}_kochliste.pdf"
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    # Remove initial empty kid rows and also from reverse
    cleaned_df = df.copy()

    # Clean from the front (beginning of dataframe)
    for i in range(len(cleaned_df)):
        if cleaned_df.iloc[i]['kid'] == '':
            continue
        else:
            # Found first non-empty kid, keep from here
            cleaned_df = cleaned_df.iloc[i:]
            break

    # Clean from the back (end of dataframe)
    for i in range(len(cleaned_df) - 1, -1, -1):
        if cleaned_df.iloc[i]['kid'] == '':
            continue
        else:
            # Found last non-empty kid, keep up to here
            cleaned_df = cleaned_df.iloc[:i + 1]
            break

    # Reset index after removing rows
    cleaned_df = cleaned_df.reset_index(drop=True)

    # Use the cleaned dataframe for the rest of the function
    df = cleaned_df

    # Create figure with the right aspect ratio for A4 landscape
    fig, ax = plt.subplots(figsize=(11.7, 8.3))  # A4 landscape in inches

    # Hide axes
    ax.axis('off')
    ax.axis('tight')

    # Convert datetime column to date format for display
    display_df = df.copy()
    if 'date' in df.columns:
        display_df['date'] = pd.to_datetime(df['date']).dt.strftime('%d.%m.%Y')

    # ===== ADJUST WRAPPING HERE =====
    # Increase these values to delay wrapping and use more horizontal space
    row_count = len(df)
    if row_count > 25:
        font_size = 8
        max_width = 147  # INCREASE THIS VALUE to delay wrapping (was 60)
    elif row_count > 15:
        font_size = 9
        max_width = 110  # INCREASE THIS VALUE to delay wrapping (was 70)
    else:
        font_size = 10
        max_width = 100  # INCREASE THIS VALUE to delay wrapping (was 80)
    # ================================

    # Apply text wrapping to dish column
    dish_col_index = 2  # Third column (0-indexed)
    for i in range(len(display_df)):
        dish_text = str(display_df.iloc[i, dish_col_index])
        # Only wrap if text is longer than max_width
        if len(dish_text) > max_width:
            display_df.iloc[i, dish_col_index] = '\n'.join(
                textwrap.wrap(dish_text, width=max_width))

    # Create table data
    table_data = display_df.values

    # Create table with renamed columns
    # Create a list of renamed column labels
    renamed_columns = ['Datum', 'Kochkind', 'Gericht']

    table = ax.table(
        cellText=table_data,
        colLabels=renamed_columns,  # Use the renamed columns here
        loc='center',
        cellLoc='center',
    )

    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(font_size)

    # Set column widths - give even more space to the dish column
    col_widths = [0.09, 0.15,
                  0.76]  # Adjusted to give more space to dish column
    for i, width in enumerate(col_widths):
        if i < 3:  # Always 3 columns
            for row in range(len(df) + 1):  # +1 for header
                table[(row, i)].set_width(width)

    # Style header - make it twice as high and use the requested color
    header_color = '#4372c9'  # Changed to requested color
    for i, key in enumerate(renamed_columns):  # Use renamed_columns here
        cell = table[(0, i)]
        cell.set_facecolor(header_color)
        cell.set_text_props(color='white', fontweight='bold')
        # Make header row twice as high
        cell.set_height(cell.get_height() * 1.5)

    # Style rows with the new color scheme
    for i in range(len(df)):
        row_idx = i + 1  # +1 because header is row 0

        # Check for empty kid field - override with dark gray
        if df.iloc[i]['kid'] == '':
            row_color = '#676767'
            # Apply row color to all columns
            for j in range(3):
                cell = table[(row_idx, j)]
                cell.set_facecolor(row_color)
        else:
            # Apply specific colors to each column
            # First column (date) - white
            table[(row_idx, 0)].set_facecolor('#FFFFFF')

            # Second column (kid) and third column (dish) - light gray
            table[(row_idx, 1)].set_facecolor('#ECECEC')
            table[(row_idx, 2)].set_facecolor('#ECECEC')

    # Apply uniform row heights to maintain alignment
    # First, find rows that need extra height due to wrapping
    row_heights = {}
    for i in range(len(df)):
        row_idx = i + 1
        text = display_df.iloc[i, dish_col_index]
        num_lines = text.count('\n') + 1
        row_heights[row_idx] = num_lines

    # Apply height adjustments uniformly
    max_lines = max(row_heights.values())
    if max_lines > 1:
        for row_idx, lines in row_heights.items():
            height_factor = 1 + (lines - 1) * 0.5
            for j in range(3):
                table[(row_idx, j)].set_height(
                    table[(row_idx, j)].get_height() * height_factor)

    # Scale table to fit the figure
    if row_count > 25:
        table.scale(1, 1.55)
    elif row_count > 15:
        table.scale(1, 1.35)
    else:
        table.scale(1, 1.3)

    # Move table down to make room for title, but not too far down
    table.set_transform(ax.transAxes)

    parot_dict = {
        'purple': '#691367',
        'light_blue': '#40B3C2',
        'orange': '#FFB203',
        'neon-red': '#EA0A5D'
    }

    # First create the logo axes with a higher z-order
    organisation_label = "./static/images/kigu_label.png"
    try:
        org_img = plt.imread(organisation_label)
        # Create a new axes for the logo in the top left with a higher z-order
        org_ax = fig.add_axes([0.51, 0.928, 0.45, 0.10], zorder=2)
        org_ax.imshow(org_img)
        org_ax.axis('off')  # Hide the axes of the logo
    except Exception as e:
        print(f"Could not load organisation label: {e}")

    # First create the logo axes with a higher z-order
    parrot_path = "./static/images/stealth_parrot.png"
    try:
        par_img = plt.imread(parrot_path)
        par_ax = fig.add_axes([-0.018, 0.93, 0.2, 0.10], zorder=2)
        par_ax.imshow(par_img)
        par_ax.axis('off')  # Hide the axes of the logo
    except Exception as e:
        print(f"Could not load parrot image: {e}")

    # Then add the suptitle with a lower z-order
    plt.suptitle(
        f"            Kochliste {month_name} {year}{' ' * (8 - len(month_name))}                                                     ",
        fontsize=21,
        fontweight=550,
        y=1,
        x=0.5,
        color='white',
        zorder=1,  # Lower z-order so it appears behind the logo
        bbox=dict(boxstyle='round,pad=0.5',
                  facecolor='#681469',
                  edgecolor=parot_dict['neon-red'],
                  alpha=0.9,
                  linewidth=5))

    # Save as PDF with landscape orientation explicitly set
    with PdfPages(pdf_path) as pdf:
        plt.tight_layout(pad=1.2)
        pdf.savefig(fig,
                    orientation='landscape',
                    bbox_inches='tight',
                    pad_inches=0.4)

    plt.close(fig)

    return pdf_path
