from datetime import datetime
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
    #score = models.IntegerField()

    def __str__(self):
        return self.name 
    

class Dish(models.Model):
    dish_name = models.CharField(max_length=500)
    cook = models.ForeignKey(Kid, on_delete=models.CASCADE)

    def __str__(self):
        return self.dish_name


class Holiday(models.Model):
    date = models.DateField()
    text = models.CharField(max_length=30, default='free')

    def __str__(self):
        return self.text

class Waiverday(models.Model):
    date = models.DateField()
    kid = models.ManyToManyField(Kid, related_name="waiverdaykids")

    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return str(self.date)


class GlobalSettings(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)

    @classmethod
    def get_current(cls):
        settings = cls.objects.first()
        if not settings:
            # Create default settings if none exist
            settings = cls.objects.create(year=2025, month=5)
        return settings
    


