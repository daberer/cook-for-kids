from django.shortcuts import render, HttpResponse
from . import settings
from .services import calculate_month, additional_holidays, additional_waiverdays, get_list_of_kids, check_correctness, optimise
import os
import json
import datetime
from .forms import WaiverdaysForm, DataframeChoice
import pandas as pd
import kochlischda.globals as globals
from .models import Dish



def home(request):
    return render(request, 'home.html')

def base(request):
    return render(request, 'base.html')

def home(request):
    return render(request, 'StaticPages/main.html')


def add_holidays(request):
    """
    #TODO: take admin input
    """
    state = additional_holidays('1-8')
    return HttpResponse(state)

def setup_month(request):
    """
    #TODO: take user input
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
            return HttpResponse(state)
        else:
            print(form.errors.as_data()) # here you print errors to terminal
    

    form = WaiverdaysForm()
    return render(request, 'waiverday_form.html', {'form': form})
    #wishdays = 0
    #kids_list = get_list_of_kids()
    #this_kid = kids_list[3]
    #state = additional_notdays('15-31', wishdays=wishdays, kid=this_kid)
    #return HttpResponse(state)

def brewing_the_kochliste(request):
    if request.method == "POST":
        form = DataframeChoice(request.POST)
        if form.is_valid():
            onetwothree = form.cleaned_data['df_number']
        if onetwothree == '1':
            df = globals.df1
        elif onetwothree == '2':
            df = globals.df2
        else:
            df = globals.df3
        
        df['dish'] = ''
        df.rename(columns={df.keys()[0]: "kid"}, inplace=True)
        for i, row in df.iterrows():
            if row.kid != '':
                if row.name.day_of_week == 4:
                    df.at[i, 'dish'] = 'Essen to go (Ausflugsessen)'
                else:
                    res = [x for x in Dish.objects.all() if x.cook.name == row.kid]
                    if not len(res):
                        df.at[i, 'dish'] = ''
                    else:
                        df.at[i, 'dish'] = str(res[0])
                
        
        ####### fill nan values of weekend days and holidays
        df['dish'].fillna('')
        
        df.to_excel(f'/home/daberer/Documents/Kochliste/{globals.year}_{globals.month}_kochliste.xlsx', sheet_name='Sheet1')

        return HttpResponse(f"successfully produced /home/daberer/Documents/Kochliste/{globals.year}_{globals.month}_kochliste.xlsx")

    scoreboard = {}
    for i in range(200):
        res = calculate_month(i)
        #ro = check_correctness(res)
        if res:
            scoreboard[i] = [res[0], res[1], res[2]]
            
    sorted_scoreboard = sorted(scoreboard.items(), key=lambda x: x[0])

    df1 = pd.DataFrame(sorted_scoreboard[0][1][2], index=['Kids (variant 1)']).transpose()
    
    df1.index = pd.to_datetime(df1.index)
    #df1 = optimise(df1)
    df1.fillna('', inplace=True)
    #df1 = ({df1.index: 32, df1.keys()[0]: str([str(a[0])+ ' ' + str(a[1]) for a in sorted_scoreboard[0][1][1].items()])})
    df2 = pd.DataFrame(sorted_scoreboard[1][1][2], index=['Kids (variant 2)']).transpose()
    df2.index = pd.to_datetime(df2.index)
    #df2 = optimise(df2)
    df2.fillna('', inplace=True)
    #df2 = df2.append({df2.index: 32, df2.keys()[0]: str([str(a[0])+ ' ' + str(a[1]) for a in sorted_scoreboard[1][1][1].items()])})
    df3 = pd.DataFrame(sorted_scoreboard[2][1][2], index=['Kids (variant 3)']).transpose()
    df3.index = pd.to_datetime(df3.index)
    #df3 = optimise(df3)
    df3.fillna('', inplace=True)
    #df3 = df3.append({df3.index: 32, df3.keys()[0]: str([str(a[0])+ ' ' + str(a[1]) for a in sorted_scoreboard[2][1][1].items()])})
    print(f'Lucky kids: \n {sorted_scoreboard[0][1][1]} \n {sorted_scoreboard[1][1][1]} \n {sorted_scoreboard[2][1][1]}')
    globals.df1 = df1
    globals.df2 = df2
    globals.df3 = df3

    form = DataframeChoice()
    #return HttpResponse(df.to_html())
    return render(request, 'result_form.html', {'resulttable1': df1.to_html(classes="dataframe dfirst"), 'resulttable2': df2.to_html(classes="dataframe dsecond"), 'resulttable3': df3.to_html(classes="dataframe dthird"), 'form': form})