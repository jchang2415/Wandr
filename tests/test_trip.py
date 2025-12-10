# Unit Tests for Trip Class

import pytest
from datetime import date
from models.activity import Activity
from models.dayplan import DayPlan
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

def test_trip_length():
    '''
    Testing to make sure trip_length() method for Trip class objects works as expected.
    '''
    t = Trip(
        destination="Chicago",
        start_date=date(2025, 12, 20),
        end_date=date(2025, 12, 22),
        budget=500,
        interests=[]
    )

    # Should be inclusive of start and end days
    assert t.trip_length() == 3


def test_trip_length_single_day():
    '''
    Test that single-day trip has length of 1
    '''
    t = Trip(
        destination="Chicago",
        start_date=date(2025, 12, 20),
        end_date=date(2025, 12, 20),
        budget=500,
        interests=[]
    )

    assert t.trip_length() == 1


def test_trip_length_week_long():
    '''
    Test week-long trip
    '''
    t = Trip(
        destination="Paris",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 7),
        budget=2000,
        interests=["museum", "food"]
    )

    assert t.trip_length() == 7


def test_trip_empty_itinerary():
    '''
    Test that trip initializes with empty itinerary
    '''
    t = Trip(
        destination="Tokyo",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 5),
        budget=1500,
        interests=["food"]
    )

    assert t.itinerary == []
    assert len(t.itinerary) == 0


def test_trip_with_itinerary():
    '''
    Test trip with itinerary added
    '''
    t = Trip(
        destination="Paris",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 2),
        budget=500,
        interests=["museum"]
    )

    day1 = DayPlan(date=date(2025, 6, 1))
    day1.add_activity(Activity("Louvre", "museum", 3.0, 20.0))
    
    day2 = DayPlan(date=date(2025, 6, 2))
    day2.add_activity(Activity("Eiffel Tower", "landmark", 2.0, 25.0))

    t.itinerary = [day1, day2]

    assert len(t.itinerary) == 2
    assert t.itinerary[0].date == date(2025, 6, 1)
    assert t.itinerary[1].date == date(2025, 6, 2)


def test_trip_to_dict():
    '''
    Test that to_dict() correctly converts Trip to dictionary
    '''
    t = Trip(
        destination="Paris",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 3),
        budget=1000,
        interests=["museum", "food"]
    )

    result = t.to_dict()

    assert result["destination"] == "Paris"
    assert result["start_date"] == "2025-06-01"
    assert result["end_date"] == "2025-06-03"
    assert result["budget"] == 1000
    assert result["interests"] == ["museum", "food"]
    assert result["itinerary"] == []


def test_trip_to_dict_with_itinerary():
    '''
    Test to_dict() with populated itinerary
    '''
    t = Trip(
        destination="Paris",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 1),
        budget=500,
        interests=["museum"]
    )

    day = DayPlan(date=date(2025, 6, 1))
    day.add_activity(Activity("Louvre", "museum", 3.0, 20.0))
    t.itinerary = [day]

    result = t.to_dict()

    assert len(result["itinerary"]) == 1
    assert result["itinerary"][0]["date"] == "2025-06-01"
    assert len(result["itinerary"][0]["activities"]) == 1


def test_trip_with_zero_budget():
    '''
    Test trip with zero budget (all free activities)
    '''
    t = Trip(
        destination="Local City",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 1),
        budget=0,
        interests=["nature"]
    )

    assert t.budget == 0


def test_trip_with_large_budget():
    '''
    Test trip with large budget
    '''
    t = Trip(
        destination="World Tour",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 30),
        budget=10000,
        interests=["museum", "food", "landmark"]
    )

    assert t.budget == 10000
    assert t.trip_length() == 30


def test_trip_with_no_interests():
    '''
    Test trip with empty interests list
    '''
    t = Trip(
        destination="Anywhere",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 1),
        budget=100,
        interests=[]
    )

    assert t.interests == []
    assert len(t.interests) == 0


def test_trip_with_many_interests():
    '''
    Test trip with many different interests
    '''
    interests = ["museum", "nature", "food", "shopping", "entertainment", "landmark"]
    
    t = Trip(
        destination="Big City",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 10),
        budget=2000,
        interests=interests
    )

    assert len(t.interests) == 6
    for interest in interests:
        assert interest in t.interests


def test_trip_date_order():
    '''
    Test that trip dates can be checked for ordering
    '''
    t = Trip(
        destination="City",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 10),
        budget=1000,
        interests=["museum"]
    )

    assert t.start_date < t.end_date


def test_trip_destinations_with_spaces():
    '''
    Test that destination names with spaces work correctly
    '''
    t = Trip(
        destination="New York City",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 3),
        budget=1500,
        interests=["museum"]
    )

    assert t.destination == "New York City"


def test_trip_destinations_with_special_characters():
    '''
    Test destinations with special characters
    '''
    t = Trip(
        destination="Montréal",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 3),
        budget=1000,
        interests=["food"]
    )

    assert t.destination == "Montréal"


def test_trip_fractional_budget():
    '''
    Test that budget can be fractional
    '''
    t = Trip(
        destination="City",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 1),
        budget=123.45,
        interests=["food"]
    )

    assert t.budget == 123.45



