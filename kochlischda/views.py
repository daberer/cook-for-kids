from django.shortcuts import render, HttpResponse
from . import settings
from .services import calculate_month, additional_holidays, additional_notdays, get_list_of_kids
import os
import json
import datetime
from .forms import NotdaysForm



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
    state = additional_holidays('15-31')
    return HttpResponse(state)

def add_notdays(request):
    """
    #TODO: take user input
    """
    if request.method == 'POST':
        form = NotdaysForm(request.POST)
        if form.is_valid():
            dates = form.cleaned_data['dates']
            kid = form.cleaned_data['kid']
            dishes_this_month = form.cleaned_data['dishes_this_month']
            wishdays = form.cleaned_data['wishdays']
            month = form.cleaned_data['month']
            year = form.cleaned_data['year']
            state = additional_notdays(days=dates, wishdays=wishdays, kid=list(kid)[0], dishes_this_month=dishes_this_month, month=month, year=year)
            return HttpResponse(state)
        else:
            print(form.errors.as_data()) # here you print errors to terminal
    

    form = NotdaysForm()
    return render(request, 'notday_form.html', {'form': form})
    #wishdays = 0
    #kids_list = get_list_of_kids()
    #this_kid = kids_list[3]
    #state = additional_notdays('15-31', wishdays=wishdays, kid=this_kid)
    #return HttpResponse(state)

def brewing_the_kochliste(request):
    scoreboard = {}
    for i in range(1000):
        res = calculate_month(i)
        if res:
            scoreboard[i] = [res[0], res[1], res[2]]
            
    #sorted_scoreboard = sorted(scoreboard.items(), key=lambda x: x[0])

    return HttpResponse(json.dumps(sorted_scoreboard))