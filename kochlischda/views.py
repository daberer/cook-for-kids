from django.shortcuts import render, HttpResponse
from . import settings
from .services import calculate_month, additional_holidays, additional_notdays, get_list_of_kids
import os
import json
import datetime



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
    wishdays = 0
    kids_list = get_list_of_kids()
    this_kid = kids_list[3]
    state = additional_notdays('15-31', wishdays=wishdays, kid=this_kid)
    return HttpResponse(state)

def brewing_the_kochliste(request):
    scoreboard = {}
    for i in range(1000):
        res = calculate_month(i)
        if res:
            scoreboard[i] = [res[0], res[1], res[2]]
            
    #sorted_scoreboard = sorted(scoreboard.items(), key=lambda x: x[0])

    return HttpResponse(json.dumps(sorted_scoreboard))