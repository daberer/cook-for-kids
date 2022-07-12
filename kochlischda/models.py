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







# class Kid():
#     """
#     Kid class represents parents cooking duty. If the kid is the designated candidate for the day, 
#     then the parents need to provide a meal from the meal list.
#     """
#     def __init__(self, name=None, exempt=False, gender='girl', monthly_dishes_number = 1):
#         self.name = name
#         self.gender = gender
#         self.exempt_from_cooking = exempt
#         self.score = 0
#         self.monthly_dishes_number = monthly_dishes_number

#     def __repr__(self):
#         if self.gender == 'girl':
#             return f'This is {self.name}, she is cooking {self.monthly_dishes_number} time(s) per month and she has a score of {str(self.score)}.'
#         return f'This is {self.name}, he is cooking {self.monthly_dishes_number} time(s) per month and she has a score of {str(self.score)}.'

#     def add_scorepoint(self):
#         self.score += 1
    
#     def subtract_scorepoint(self):
#         self.score -= 1

#     def score(self):
#         return self.score




# class Dish():
#     """
#     """
#     def __init__(self, name):
#         self.name = name


# class Rules():
#     def __init__(self, days_between_two_meals_weight = 4, avoid_twice_per_week = 5):
#         self.maximum_days_between_two_meals = days_between_two_meals_weight
#         self.no_cooking_in_same_week = avoid_twice_per_week








# class LegalHoliday(db.Model):
#     """
#         Class for legal holidays. Needs to be updated in the
#         database every year.
#     """
#     __tablename__ = 'legal_holiday'
#     id = db.Column(db.Integer, primary_key=True)
#     holiday = db.Column(db.DateTime)
#     name = db.Column(db.String(255))
#     version = db.Column(db.Integer, nullable=False)
