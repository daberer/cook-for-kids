import pytest
from cook_for_kids.services import calculate_month
from datetime import datetime
from cook_for_kids.models import Kid
import io
import sys

@pytest.mark.django_db
def test_calculation(kids, dishes, holidays, waiverdays):
    result = calculate_month(it=1, test=True)
    
    assert isinstance(result, tuple)
    assert len(result) == 3
    assert isinstance(result[1], dict)
    total_lucky_kids_count = sum(result[1].values())
    assert total_lucky_kids_count == 2

    assert isinstance(result[2], dict)


    for date_str, assigned_kid in result[2].items():
        date_obj = datetime.strptime(date_str, "%m/%d/%Y")
        weekday = date_obj.weekday()

        # Saturday (5) and Sunday (6) should have None assignments
        if weekday in [5, 6]:
            assert assigned_kid is None, f"Expected None on weekend {date_str}, got {assigned_kid}"


    assigned_days = [day for day, kid in result[2].items() if kid is not None]
    none_days = [day for day, kid in result[2].items() if kid is None]
    weekdays_in_month = len(result[2]) - len(none_days)
    assert len(assigned_days) == weekdays_in_month

    
    assigned_kids = [kid for kid in result[2].values() if kid is not None]
    for kid_name in assigned_kids:
        assert Kid.objects.filter(name=kid_name).exists(), \
            f"Assigned kid '{kid_name}' not found in database"

    # May 2025 has 31 days
    assert len(result[2]) == 31

    for date_str in result[2].keys():
        try:
            datetime.strptime(date_str, "%m/%d/%Y")
            assert True
        except ValueError:
            assert False, f"Invalid date format: {date_str}"



@pytest.mark.django_db
def test_failed_calculation(kids, dishes, holidays, waiverdays):
    # Remove 3 kids from the database
    kid_names_to_remove = ['lily', 'rango', 'michelle']

    for name in kid_names_to_remove:
        kid = Kid.objects.filter(name=name).first()
        if kid:
            kid.delete()

    # Verify we now have fewer kids
    assert Kid.objects.count() == 8

    # Capture stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output

    result = calculate_month(it=1, test=True)
    assert result is None

    # Get the captured output
    output = captured_output.getvalue()
    # Check for the specific error message
    assert "Not enough Kochdienste (16), for 20 Kochtage this month." in output

    