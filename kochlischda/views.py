from django.shortcuts import render, HttpResponse, redirect
from . import settings
from .services import calculate_month, additional_holidays, additional_waiverdays, get_list_of_kids, check_correctness_df, optimise
import json
from .forms import WaiverdaysForm, DataframeChoice, AdditionalHolidaysForm
import pandas as pd
from kochlischda.globals import Setup
from .models import Dish

from django.urls import reverse
from django.conf import settings
from django.http import FileResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages

from .globals import Setup


def home(request):
    return render(request, 'home.html')

def base(request):
    return render(request, 'base.html')

def home(request):
    return render(request, 'StaticPages/main.html')


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
    return render(request, 'additional_holiday_form.html', {'form': form, 'month': Setup.month})

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
            state = additional_waiverdays(days=dates, wishdays=wishdays, kid=list(kid)[0], dishes_this_month=dishes_this_month, month=month, year=year, dish=dish)
            messages.success(request, state)
            return redirect(setup_month)
        else:
            messages.error(request, "There was an error with your form submission.")

    
    form = WaiverdaysForm()
    return render(request, 'waiverday_form.html', {'form': form})
    #wishdays = 0
    #kids_list = get_list_of_kids()
    #this_kid = kids_list[3]
    #state = additional_notdays('15-31', wishdays=wishdays, kid=this_kid)
    #return HttpResponse(state)

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
            response = {'message': f'for df1: {check_correctness_df(df1)}, for df2: {check_correctness_df(df2)}, for df3: {check_correctness_df(df3)}'}
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
            return render(request, 'result_form.html', {'resulttable1': df1.to_html(classes="dataframe dfirst"), 'resulttable2': df2.to_html(classes="dataframe dsecond"), 'resulttable3': df3.to_html(classes="dataframe dthird"), 'form': form})


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
        for i, row in df.iterrows():
            if row.kid != '':
                if row.name.day_of_week == 1:
                    df.at[i, 'dish'] = 'Essen to go (Ausflugsessen)'
                else:
                    res = [x for x in Dish.objects.all() if x.cook.name == row.kid]
                    if not len(res):
                        df.at[i, 'dish'] = ''
                    else:   
                        df.at[i, 'dish'] = str(res[0])

                    
        
        ####### fill nan values of weekend days and holidays
        df['dish'].fillna('')
        
        df.reset_index(inplace=True)
        
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

    df1 = pd.DataFrame(sorted_scoreboard[0][1][2], index=['Kids (variant 1)']).transpose()
    
    df1.index = pd.to_datetime(df1.index)
    if Setup.optimise:
        df1 = optimise(df1)
    df1.fillna('', inplace=True)
    #df1 = ({df1.index: 32, df1.keys()[0]: str([str(a[0])+ ' ' + str(a[1]) for a in sorted_scoreboard[0][1][1].items()])})
    df2 = pd.DataFrame(sorted_scoreboard[1][1][2], index=['Kids (variant 2)']).transpose()
    df2.index = pd.to_datetime(df2.index)
    if Setup.optimise:
        df2 = optimise(df2)
    df2.fillna('', inplace=True)
    #df2 = df2.append({df2.index: 32, df2.keys()[0]: str([str(a[0])+ ' ' + str(a[1]) for a in sorted_scoreboard[1][1][1].items()])})
    df3 = pd.DataFrame(sorted_scoreboard[2][1][2], index=['Kids (variant 3)']).transpose()
    df3.index = pd.to_datetime(df3.index)
    if Setup.optimise:
        df3 = optimise(df3)
    df3.fillna('', inplace=True)
    #df3 = df3.append({df3.index: 32, df3.keys()[0]: str([str(a[0])+ ' ' + str(a[1]) for a in sorted_scoreboard[2][1][1].items()])})
    print(f'Lucky kids: \n {sorted_scoreboard[0][1][1]} \n {sorted_scoreboard[1][1][1]} \n {sorted_scoreboard[2][1][1]}')
    Setup.df1 = df1
    Setup.df2 = df2
    Setup.df3 = df3

    form = DataframeChoice()
    return render(request, 'result_form.html', {'resulttable1': df1.to_html(classes="dataframe dfirst"), 'resulttable2': df2.to_html(classes="dataframe dsecond"), 'resulttable3': df3.to_html(classes="dataframe dthird"), 'form': form})