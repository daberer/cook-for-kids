import pytest
from datetime import date, timedelta
from cook_for_kids.models import Kid, Dish, Holiday, Waiverday

@pytest.fixture
def kids():
    """Create 10 test kids with different attributes"""
    kids_data = []
    names = sorted(['lily', 'rango', 'michelle', 'mercedes', 'shrek', 'munchkin', 'dubuos', 'humpy', 'fry', 'charlie', 'vaiana'])
    for i in range(0, 11):
        kid = Kid.objects.create(
            name=f"{names[i]}",
            exempt=False,  
            monthly_dishes=2  # 1-4 dishes per month
        )
        kids_data.append(kid)
    return kids_data

@pytest.fixture
def dishes(kids):
    """Create a dish for each kid"""
    dishes_data = []
    for i, kid in enumerate(kids):
        dish = Dish.objects.create(
            dish_name=f"Test Dish {i+1}",
            cook=kid
        )
        dishes_data.append(dish)
    return dishes_data

@pytest.fixture
def holidays():
    """Create some test holidays"""
    holidays_data = []
    today = date.today()
    for i in range(3):
        holiday = Holiday.objects.create(
            date=today + timedelta(days=i*7),
            text=f"Holiday {i+1}"
        )
        holidays_data.append(holiday)
    return holidays_data

@pytest.fixture
def waiverdays(kids):
    """Create some test waiver days with associated kids"""
    waiverdays_data = []
    today = date.today()
    for i in range(5):
        waiver = Waiverday.objects.create(
            date=today + timedelta(days=i*3)
        )
        # Assign random kids to each waiver day
        waiver.kid.add(kids[i % len(kids)])
        if i % 4 == 0:  # Add a second kid to every other waiver day
            waiver.kid.add(kids[(i+1) % len(kids)])
        waiverdays_data.append(waiver)
    return waiverdays_data
