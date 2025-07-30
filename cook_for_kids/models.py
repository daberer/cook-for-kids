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
    WEEKDAY_CHOICES = [
        (None, 'No weekly excursion'),
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
    ]

    # Mapping dictionary for easy access
    WEEKDAY_NAMES = {
        0: 'Monday',
        1: 'Tuesday', 
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday'
    }

    year = models.IntegerField()
    month = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    excursion_day = models.IntegerField(
        choices=WEEKDAY_CHOICES,
        null=True,
        blank=True,
        default=1,  # Tuesday
        help_text="Day of the week for excursions (leave empty for no weekly excursion)"
    )
    weekly_event_text = models.CharField(
        max_length=100,
        default='Essen to go (Ausflugsessen)',
        help_text="Text to display for weekly excursion meals"
    )

    @classmethod
    def get_current(cls):
        settings = cls.objects.first()
        if not settings:
            # Create default settings if none exist
            settings = cls.objects.create(
                year=2025, 
                month=5, 
                excursion_day=1,
                weekly_event_text='Essen to go (Ausflugsessen)'
            )
        return settings

    @property
    def excursion_day_name(self):
        """Returns the human-readable name of the excursion day"""
        if self.excursion_day is None:
            return 'No weekly excursion'
        return self.WEEKDAY_NAMES.get(self.excursion_day, 'Unknown')

    @property
    def has_weekly_excursion(self):
        """Returns True if a weekly excursion day is set"""
        return self.excursion_day is not None

    def __str__(self):
        if self.has_weekly_excursion:
            return f"Excursions on {self.excursion_day_name}"
        else:
            return f"No weekly excursions"

    class Meta:
        verbose_name = "Global Settings"
        verbose_name_plural = "Global Settings"


