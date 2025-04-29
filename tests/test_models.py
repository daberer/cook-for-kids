import pytest
from cook_for_kids.models import Kid, Dish, Holiday, Waiverday

@pytest.mark.django_db
def test_kid_creation(kids):
    """Test that kids are created correctly"""
    assert len(kids) == 11
    assert Kid.objects.count() == 11
    assert kids[4].name == "lily"
    assert kids[7].name == "munchkin"
    assert kids[2].exempt is False

@pytest.mark.django_db
def test_dish_assignment(dishes, kids):
    """Test that dishes are assigned to kids correctly"""
    assert len(dishes) == 11
    assert Dish.objects.count() == 11
    # Check that each dish is assigned to the correct kid
    for i, dish in enumerate(dishes):
        assert dish.cook == kids[i]

@pytest.mark.django_db
def test_waiverday_relationships(waiverdays, kids):
    """Test the many-to-many relationship between waiverdays and kids"""
    assert len(waiverdays) == 5
    # Check that waiver days have the correct number of kids
    for i, waiver in enumerate(waiverdays):
        if i % 4 == 0:
            assert waiver.kid.count() == 2
        else:
            assert waiver.kid.count() == 1
