from operator import mod
from django.db import models


class Kid(models.Model):
    """
    Kid class represents parents cooking duty. If the kid is the designated candidate for the day, 
    then the parents need to provide a meal from the meal list.
    """
    name = models.CharField(max_length=25)
    exempt = models.BooleanField()
    monthly_dishes = models.IntegerField()
    score = models.IntegerField()

    def __str__(self):
        return self.name
    
    


class Dish(models.Model):
    dish_name = models.CharField(max_length=100)
    cook = models.ForeignKey(Kid, on_delete=models.CASCADE)

    def __str__(self):
        return self.dish_name



class Holiday(models.Model):
    date = models.DateTimeField()
    text = models.CharField(max_length=30)


