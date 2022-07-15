from django.shortcuts import render, HttpResponse
from . import settings
import os
from .services import calculate_month
import json
import datetime



def home(request):
    return render(request, 'home.html')

def base(request):
    return render(request, 'base.html')

def home(request):
    return render(request, 'StaticPages/main.html')

def brewing_the_kochliste(request):
    scoreboard = {}
    for i in range(1000):
        res = calculate_month()
        scoreboard[res[0]] = res[1]
    sorted_scoreboard = dict(sorted(scoreboard.items()))

    return HttpResponse(json.dumps(sorted_scoreboard))