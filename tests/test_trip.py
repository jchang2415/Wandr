# Unit Tests for Trip Class

from datetime import date
from models.trip import Trip

def test_trip_initialization():
    '''
    Test Trip class object initialization
    '''
    # Initialize test Trip class object
    t = Trip(
        destination="Chicago",
        start_date=date(2025, 12, 20),
        end_date=date(2025, 12, 22),
        budget=500,
        interests=["museum", "nature"]
    )

    # Check attributes of test object
    assert t.destination == "Chicago"
    assert t.start_date == date(2025, 12, 20)
    assert t.end_date == date(2025, 12, 22)
    assert t.budget == 500
    assert "nature" in t.interests

def test_trip_duration_days():
    '''
    Testing to make sure duration_days() method for Trip class objects works as expected.
    '''
    # Initialize test Trip class object
    t = Trip(
        destination="Chicago",
        start_date=date(2025, 12, 20),
        end_date=date(2025, 12, 22),
        budget=500,
        interests=[]
    )

    # Check duration_days() method outputs expected result; is inclusive of start and end days
    assert t.duration_days() == 3  