from django.shortcuts import render, HttpResponse
from . import settings
from .services import calculate_month, additional_holidays, additional_waiverdays, get_list_of_kids, check_correctness, optimise
import os
import json
import datetime
from .forms import WaiverdaysForm
import pandas as pd



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
    state = additional_holidays('24-31')
    return HttpResponse(state)

def add_waiverdays(request):
    """
    #TODO: take user input
    """
    if request.method == 'POST':
        form = WaiverdaysForm(request.POST)
        if form.is_valid():
            dates = form.cleaned_data['dates']
            kid = form.cleaned_data['kid']
            dishes_this_month = form.cleaned_data['dishes_this_month']
            wishdays = form.cleaned_data['wishdays']
            month = form.cleaned_data['month']
            year = form.cleaned_data['year']
            state = additional_waiverdays(days=dates, wishdays=wishdays, kid=list(kid)[0], dishes_this_month=dishes_this_month, month=month, year=year)
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
    scoreboard = {}
    for i in range(50):
        res = calculate_month(i)
        #ro = check_correctness(res)
        if res:
            scoreboard[i] = [res[0], res[1], res[2]]
            
    sorted_scoreboard = sorted(scoreboard.items(), key=lambda x: x[0])

    df1 = pd.DataFrame(sorted_scoreboard[0][1][2], index=['Kids (variant 1)']).transpose()
    df1.index = pd.to_datetime(df1.index)
    df1 = optimise(df1)
    df2 = pd.DataFrame(sorted_scoreboard[1][1][2], index=['Kids (variant 2)']).transpose()
    df2.index = pd.to_datetime(df2.index)
    df2 = optimise(df2)
    df3 = pd.DataFrame(sorted_scoreboard[2][1][2], index=['Kids (variant 3)']).transpose()
    df3.index = pd.to_datetime(df3.index)
    df3 = optimise(df3)

    
    #return HttpResponse(df.to_html())
    return render(request, 'result_form.html', {'resulttable1': df1.to_html(classes="dataframe dfirst"), 'resulttable2': df2.to_html(classes="dataframe dsecond"), 'resulttable3': df3.to_html(classes="dataframe dthird")})