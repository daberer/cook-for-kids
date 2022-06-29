from django.shortcuts import render, HttpResponse
from . import settings
import os

import calendar
import datetime

def home(request):
    return render(request, 'home.html')

def brewing_the_kochliste(request):
    currentDate = datetime.date.today()
    daysInMonth= calendar.monthrange(currentDate.year, currentDate.month)[1]
    print(currentDate)
    print(daysInMonth)

    return HttpResponse('success')
