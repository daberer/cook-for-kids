from django.shortcuts import render, HttpResponse, redirect
from .services import calculate_month, add_or_subtract_holidays, additional_waiverdays, \
        get_cooking_schedule, check_correctness_df, optimize_schedule as optimise, num_days_in_month, \
        get_kid_dates_dict, create_styled_pdf, get_holidays_this_month, \
        validate_holiday_format
import json
from .forms import WaiverdaysForm, AdditionalHolidaysForm
import pandas as pd
from cook_for_kids.globals import Setup
from .models import Dish, GlobalSettings
from django.http import FileResponse, JsonResponse
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import GlobalSettings
from django.contrib.auth.decorators import login_required
from cook_for_kids.settings import PDF_DIR

def is_staff_user(user):
    return user.is_staff

@login_required
def home(request):
    settings = GlobalSettings.get_current()
    year = settings.year
    month = settings.month
    num_days = num_days_in_month(year, month)
    cooking_data = get_cooking_schedule(year, month, num_days)
    return render(request, 'base.html', {'cooking_data': cooking_data})


@login_required
def setup_month(request):
    """
    #
    """
    settings = GlobalSettings.get_current()
    year = settings.year
    month = settings.month
    if request.method == 'POST' and 'holiday_submit' in request.POST:
        holiday_form = AdditionalHolidaysForm(request.POST)
        if holiday_form.is_valid():
            dates = holiday_form.cleaned_data['dates']

            # Validate the format of the dates string
            is_valid, error_message = validate_holiday_format(dates)

            if is_valid:
                state = add_or_subtract_holidays(dates)
                if state.startswith('Success'):
                    messages.success(request, f"Holidays updated successfully. {state}")
                else:
                    messages.error(request, f"Error updating holidays: {state}")
            else:
                messages.error(request, f"Invalid date format. {error_message}. Please use format like '1,2,10-15,18-19'")
        else:
            messages.error(request, "Invalid form submission. Please check your inputs.")
        return redirect(setup_month)
    elif request.method == 'POST':
        form = WaiverdaysForm(request.POST)
        if form.is_valid():
            dates = form.cleaned_data['dates']
            kid = form.cleaned_data['kid']
            dishes_this_month = form.cleaned_data['dishes_this_month']
            dish = form.cleaned_data['dish']
            wishdays = form.cleaned_data['wishdays']
            month = form.cleaned_data['month']
            year = form.cleaned_data['year']
            state = additional_waiverdays(days=dates,
                                          wishdays=wishdays,
                                          kid=kid,
                                          dishes_this_month=dishes_this_month,
                                          month=month,
                                          year=year,
                                          dish=dish)
            messages.success(request, state)
            return redirect(setup_month)
        else:
            messages.error(request,
                           "There was an error with your form submission.")

    num_days = num_days_in_month(year, month)
    cooking_data = get_cooking_schedule(year, month, num_days)
    kid_dates_dict = get_kid_dates_dict(year, month)
    form = WaiverdaysForm(initial={
        'year': str(year),
        'month': str(month)
    })

    holidays = get_holidays_this_month(year, month)
    holiday_form = AdditionalHolidaysForm()
    return render(
        request, 'waiverday_form.html', {
            'form': form,
            'holiday_form': holiday_form,
            'cooking_data': cooking_data,
            'kid_dates_dict': kid_dates_dict,
            'monthly_holidays': holidays
        })


@login_required
def check_results(request):
    if request.method == "POST":
        swap_data = request.POST.get('swapData')
        if swap_data == '':
            response = {'message': 'No changes in the results - table!'}
            return JsonResponse(response, status=200)
        else:
            swap_data = json.loads(swap_data)
            # Load your DataFrames here or define them as needed
            df = Setup.df
            if 'df' in swap_data:
                df.iloc[:, 0] = swap_data['df']
            response = {
                'message':
                f'{check_correctness_df(df)}'
            }
            return JsonResponse(response, status=200)


@login_required
def brewing_the_kochliste(request):
    settings = GlobalSettings.get_current()
    year = settings.year
    month = settings.month
    
    
    if request.method == "POST":
        swap_data = request.POST.get('swapData')
        # Start with the default dataframe
        df = Setup.df.copy(deep=True)

        # Apply swap data if present
        if swap_data:
            swap_data = json.loads(swap_data)
            if 'df' in swap_data:
                df.iloc[:, 0] = swap_data['df']

        # Process the dataframe
        df['dish'] = ''
        df.rename(columns={df.keys()[0]: "kid"}, inplace=True)

        # Filter out rows where the index starts with "SubBench"
        df = df[~df.index.astype(str).str.startswith('SubBench')]
        df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
        for i, row in df.iterrows():
            if row.kid != '':
                settings = GlobalSettings.get_current()
                if (settings.has_weekly_excursion and 
                    row.name.day_of_week == settings.excursion_day):
                    df.at[i, 'dish'] = settings.weekly_event_text
                else:
                    res = [x for x in Dish.objects.all() if x.cook.name == row.kid]
                    if not len(res):
                        df.at[i, 'dish'] = ''
                    else:
                        df.at[i, 'dish'] = str(res[0])

        ####### fill nan values of weekend days and holidays
        df['dish'].fillna('')

        df.reset_index(inplace=True, names=['date'])

        styled_weasyprint_output = True
        if styled_weasyprint_output:
            pdf_path = create_styled_pdf(df)
            return FileResponse(open(pdf_path, 'rb'))

        else:
            path_to_csv = f'{PDF_DIR}/{year}_{month}_kochliste.csv'
            df.to_csv(path_to_csv, sep=",", index=False, header=None)

            return FileResponse(open(path_to_csv, 'rb'))

    scoreboard = {}
    breakout = 1
    while len(scoreboard) < 1:
        res = calculate_month(breakout)
        #ro = check_correctness(res)
        breakout += 1
        if breakout == Setup.trial_number:
            return HttpResponse('No solution found. Check Sperrtage.')
        if res:
            scoreboard[breakout] = [res[0], res[1], res[2]]

    sorted_scoreboard = sorted(scoreboard.items(), key=lambda x: x[0])

    # Function to process a single dataframe
    def process_df(scoreboard_data, variant_name):
        # Create initial dataframe
        df = pd.DataFrame(scoreboard_data[1][2],
                          index=[f'Kids'
                                 ]).transpose()
        df.index = pd.to_datetime(
            df.index)  #the optimisation requires datetime format
        if Setup.optimise:
            df = optimise(df)
        df.fillna('', inplace=True)

        df.index = df.index.astype(str)
        # Add SubBench entries based on the dictionary values
        lucky_kids_dict = scoreboard_data[1][1]
        bench_counter = 1
        for kid_name, count in lucky_kids_dict.items():
            # Add the kid to SubBench rows as many times as the count indicates
            for i in range(count):
                bench_key = f'SubBench{bench_counter}'
                df.loc[bench_key] = [kid_name]
                bench_counter += 1

        return df

    # Process dataframe
    df = process_df(sorted_scoreboard[0], '1')

    # Print lucky kids
    print(
        f'Lucky kids: \n {sorted_scoreboard[0][1][1]}'
    )

    # Store dataframes in Setup
    Setup.df = df

    # Create form and render template
    return render(
        request, 'result_form.html', {
            'resulttable': df.to_html(classes="dataframe dfirst")
        })

@require_POST
@login_required
def update_global_date(request):
    year = int(request.POST.get('year'))
    month = int(request.POST.get('month'))

    settings = GlobalSettings.get_current()
    settings.year = year
    settings.month = month
    settings.save()

    return JsonResponse({
        'success': True,
        'should_refresh': settings.year != year or settings.month != month
    })