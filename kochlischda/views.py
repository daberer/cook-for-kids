from django.shortcuts import render, HttpResponse
from . import settings
import os
from .services import calculate_month




def home(request):
    return render(request, 'home.html')

def base(request):
    return render(request, 'base.html')

def home(request):
    return render(request, 'StaticPages/main.html')

def brewing_the_kochliste(request):

    calculate_month()
    return HttpResponse('success')