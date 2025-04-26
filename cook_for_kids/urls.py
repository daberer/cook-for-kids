"""cook_for_kids URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.views.generic.base import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    #path('', views.home, name='home'),
    path('start/', views.brewing_the_kochliste, name='brewing'),
    path('base/', views.base, name='base'),
    path('addholidays/', views.add_holidays, name='add holidays'),
    path('setup-month/', views.setup_month, name='setup month'),
    path('check-results/', views.check_results, name='check results'),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),]
    
