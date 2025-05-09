from django.shortcuts import render, HttpResponse, redirect
from . import settings
from .services import calculate_month, additional_holidays, additional_waiverdays, \
        get_cooking_schedule, check_correctness_df, optimise, num_days_in_month, \
        get_kid_dates_dict, create_styled_pdf
import json
from .forms import WaiverdaysForm, DataframeChoice, AdditionalHolidaysForm
import pandas as pd
from cook_for_kids.globals import Setup
from .models import Dish

from django.urls import reverse
from django.conf import settings
from django.http import FileResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from .globals import Setup


def home(request):
    num_days = num_days_in_month(Setup.year, Setup.month)
    cooking_data = get_cooking_schedule(Setup.year, Setup.month, num_days)
    return render(request, 'home.html', {'cooking_data': cooking_data})


def add_holidays(request):
    """
    #
    """
    if request.method == 'POST':
        form = AdditionalHolidaysForm(request.POST)
        if form.is_valid():
            dates = form.cleaned_data['dates']
            state = additional_holidays(dates)
            return HttpResponse(state)
        else:
            print(form.errors.as_data())
    form = AdditionalHolidaysForm()
    return render(request, 'additional_holiday_form.html', {
        'form': form,
        'month': Setup.month
    })


def setup_month(request):
    """
    #
    """
    if request.method == 'POST':
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

    num_days = num_days_in_month(Setup.year, Setup.month)
    cooking_data = get_cooking_schedule(Setup.year, Setup.month, num_days)
    kid_dates_dict = get_kid_dates_dict(Setup.year, Setup.month)
    form = WaiverdaysForm()
    return render(
        request, 'waiverday_form.html', {
            'form': form,
            'cooking_data': cooking_data,
            'kid_dates_dict': kid_dates_dict
        })


def check_results(request):
    if request.method == "POST":
        swap_data = request.POST.get('swapData')
        if swap_data == '':
            response = {'message': 'No changes in the results - table!'}
            return JsonResponse(response, status=200)
        else:
            swap_data = json.loads(swap_data)
            # Load your DataFrames here or define them as needed
            df1 = Setup.df1
            df2 = Setup.df2
            df3 = Setup.df3
            if 'df1' in swap_data:
                df1.iloc[:, 0] = swap_data['df1']
            if 'df2' in swap_data:
                df2.iloc[:, 0] = swap_data['df2']
            if 'df3' in swap_data:
                df3.iloc[:, 0] = swap_data['df3']
            response = {
                'message':
                f'for Table 1: {check_correctness_df(df1)}, for Table 2: {check_correctness_df(df2)}, for Table 3: {check_correctness_df(df3)}'
            }
            return JsonResponse(response, status=200)


def brewing_the_kochliste(request):
    if request.method == "POST":
        swap_data = request.POST.get('swapData')
        if swap_data:
            swap_data = json.loads(swap_data)
            # Load your DataFrames here or define them as needed
            df1 = Setup.df1
            df2 = Setup.df2
            df3 = Setup.df3

            # Update only the first column with swapped data
            if 'df1' in swap_data:
                df1.iloc[:, 0] = swap_data['df1']
            if 'df2' in swap_data:
                df2.iloc[:, 0] = swap_data['df2']
            if 'df3' in swap_data:
                df3.iloc[:, 0] = swap_data['df3']
            form = DataframeChoice()
            return render(
                request, 'result_form.html', {
                    'resulttable1': df1.to_html(classes="dataframe dfirst"),
                    'resulttable2': df2.to_html(classes="dataframe dsecond"),
                    'resulttable3': df3.to_html(classes="dataframe dthird"),
                    'form': form
                })

        form = DataframeChoice(request.POST)
        if form.is_valid():
            onetwothree = form.cleaned_data['df_number']
        if onetwothree == '1':
            df = Setup.df1.copy(deep=True)
        elif onetwothree == '2':
            df = Setup.df2.copy(deep=True)
        else:
            df = Setup.df3.copy(deep=True)

        df['dish'] = ''
        df.rename(columns={df.keys()[0]: "kid"}, inplace=True)

        # Filter out rows where the index starts with "SubBench"
        df = df[~df.index.astype(str).str.startswith('SubBench')]
        df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
        for i, row in df.iterrows():
            if row.kid != '':
                if row.name.day_of_week == Setup.excursion_day[1] and Setup.excursion_day[0]:
                    df.at[i, 'dish'] = 'Essen to go (Ausflugsessen)'
                else:
                    res = [
                        x for x in Dish.objects.all() if x.cook.name == row.kid
                    ]
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
            path_to_csv = f'/home/daberer/Documents/Kochliste/{Setup.year}_{Setup.month}_kochliste.csv'
            df.to_csv(path_to_csv, sep=",", index=False, header=None)

            return FileResponse(open(path_to_csv, 'rb'))

    scoreboard = {}
    breakout = 1
    while len(scoreboard) < 3:
        res = calculate_month(breakout)
        #ro = check_correctness(res)
        breakout += 1
        if breakout == Setup.trial_number:
            return HttpResponse('No three solutions found.')
        if res:
            scoreboard[breakout] = [res[0], res[1], res[2]]

    sorted_scoreboard = sorted(scoreboard.items(), key=lambda x: x[0])

    # Function to process a single dataframe
    def process_df(scoreboard_data, variant_name):
        # Create initial dataframe
        df = pd.DataFrame(scoreboard_data[1][2],
                          index=[f'Kids (variant {variant_name})'
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

    # Process each dataframe
    df1 = process_df(sorted_scoreboard[0], '1')
    df2 = process_df(sorted_scoreboard[1], '2')
    df3 = process_df(sorted_scoreboard[2], '3')

    # Print lucky kids
    print(
        f'Lucky kids: \n {sorted_scoreboard[0][1][1]} \n {sorted_scoreboard[1][1][1]} \n {sorted_scoreboard[2][1][1]}'
    )

    # Store dataframes in Setup
    Setup.df1 = df1
    Setup.df2 = df2
    Setup.df3 = df3

    # Create form and render template
    form = DataframeChoice()
    return render(
        request, 'result_form.html', {
            'resulttable1': df1.to_html(classes="dataframe dfirst"),
            'resulttable2': df2.to_html(classes="dataframe dsecond"),
            'resulttable3': df3.to_html(classes="dataframe dthird"),
            'form': form
        })
