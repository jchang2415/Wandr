# Unit Testing for DayPlan 

import pytest
from datetime import date
from models.dayplan import DayPlan
from models.activity import Activity

def test_dayplan_initialization():
    '''
    Testing initialization of DayPlan class objects and all attributes.
    '''

    # Initialize test DayPlan object
    day = DayPlan(date=date(2025, 1, 1))

    # Test attributes of test DayPlan class object
    assert day.date == date(2025, 1, 1)
    assert day.activities == []

def test_dayplan_add_activity():
    '''
    Testing add_activity method of DayPlan class objects.
    '''
    # Initialize test DayPlan class object and test Activity class object
    day = DayPlan(date=date(2025, 1, 1))
    a = Activity("Zoo", "nature", 3.0, 15.0, (21.4, 32.4), "Test")

    # Attempt to use add_activity method of DayPlan class object
    day.add_activity(a)

    # Check that activity was added correctly to DayPlan object
    assert len(day.activities) == 1
    assert day.activities[0].name == "Zoo"

def test_dayplan_add_multiple_activities():
    '''
    Test adding multiple activities to a single day
    '''
    day = DayPlan(date=date(2025, 1, 1))
    a1 = Activity("Museum", "museum", 2.0, 20.0, (21.4, 32.4), "Test")
    a2 = Activity("Park", "nature", 1.0, 0.0, (21.4, 32.4), "Test")
    a3 = Activity("Restaurant", "food", 1.5, 30.0, (21.4, 32.4), "Test")

    day.add_activity(a1)
    day.add_activity(a2)
    day.add_activity(a3)

    assert len(day.activities) == 3
    assert day.activities[0].name == "Museum"
    assert day.activities[1].name == "Park"
    assert day.activities[2].name == "Restaurant"
    

def test_dayplan_total_duration():
    '''
    Test that the total_duration() method of DayPlan class objects works.
    '''
    # Initialize test DayPlan class object with two sample activities
    day = DayPlan(date=date(2025, 1, 1))
    day.add_activity(Activity("Museum", "museum", 2.0, 20.0, (21.4, 32.4), "Test"))
    day.add_activity(Activity("Park", "nature", 1.0, 0.0, (21.4, 32.4), "Test"))

    # Check output of total_duration() method is as expected

    assert day.total_duration() == 3.0

def test_dayplan_total_cost():
    '''
    Test that total_cost() correctly sums activity prices
    '''
    day = DayPlan(date=date(2025, 1, 1))
    day.add_activity(Activity("Museum", "museum", 2.0, 20.0, (21.4, 32.4), "Test"))
    day.add_activity(Activity("Park", "nature", 1.0, 0.0, (21.4, 32.4), "Test"))
    day.add_activity(Activity("Restaurant", "food", 1.5, 35.0, (21.4, 32.4), "Test"))

    assert day.total_cost() == 55.0


def test_dayplan_empty_totals():
    '''
    Test that empty day has zero totals
    '''
    day = DayPlan(date=date(2025, 1, 1))

    assert day.total_duration() == 0.0
    assert day.total_cost() == 0.0


def test_dayplan_to_dict():
    '''
    Test that to_dict() correctly converts DayPlan to dictionary
    '''
    day = DayPlan(date=date(2025, 1, 1))
    day.add_activity(Activity("Museum", "museum", 2.0, 20.0, (21.4, 32.4), "Test"))
    day.add_activity(Activity("Park", "nature", 1.0, 0.0, (21.4, 32.4), "Test"))

    result = day.to_dict()

    assert result["date"] == "2025-01-01"
    assert len(result["activities"]) == 2
    assert result["activities"][0]["name"] == "Museum"
    assert result["activities"][1]["name"] == "Park"


def test_dayplan_to_dict_empty():
    '''
    Test that to_dict() works for empty day
    '''
    day = DayPlan(date=date(2025, 1, 1))

    result = day.to_dict()

    assert result["date"] == "2025-01-01"
    assert result["activities"] == []


def test_dayplan_with_free_activities():
    '''
    Test day with only free activities
    '''
    day = DayPlan(date=date(2025, 1, 1))
    day.add_activity(Activity("Park", "nature", 1.0, 0.0, (21.4, 32.4), "Test"))
    day.add_activity(Activity("Walk", "nature", 1.5, 0.0, (21.4, 32.4), "Test"))

    assert day.total_cost() == 0.0
    assert day.total_duration() == 2.5


def test_dayplan_with_expensive_activities():
    '''
    Test day with expensive activities
    '''
    day = DayPlan(date=date(2025, 1, 1))
    day.add_activity(Activity("Show", "entertainment", 2.5, 150.0, (21.4, 32.4), "Test"))
    day.add_activity(Activity("Fine Dining", "food", 2.0, 100.0, (21.4, 32.4), "Test"))

    assert day.total_cost() == 250.0


def test_dayplan_different_dates():
    '''
    Test that different DayPlans can have different dates
    '''
    day1 = DayPlan(date=date(2025, 1, 1))
    day2 = DayPlan(date=date(2025, 1, 2))

    assert day1.date != day2.date


def test_dayplan_activities_order_preserved():
    '''
    Test that activities maintain their order
    '''
    day = DayPlan(date=date(2025, 1, 1))
    a1 = Activity("First", "museum", 1.0, 10.0, (21.4, 32.4), "Test")
    a2 = Activity("Second", "nature", 1.0, 0.0, (21.4, 32.4), "Test")
    a3 = Activity("Third", "food", 1.0, 20.0, (21.4, 32.4), "Test")

    day.add_activity(a1)
    day.add_activity(a2)
    day.add_activity(a3)

    assert day.activities[0].name == "First"
    assert day.activities[1].name == "Second"
    assert day.activities[2].name == "Third"


def test_dayplan_with_fractional_hours():
    '''
    Test that DayPlan correctly handles fractional hours
    '''
    day = DayPlan(date=date(2025, 1, 1))
    day.add_activity(Activity("Quick Visit", "museum", 0.5, 10.0, (21.4, 32.4), "Test"))
    day.add_activity(Activity("Snack", "food", 0.25, 5.0, (21.4, 32.4), "Test"))

    assert day.total_duration() == 0.75


def test_dayplan_activity_count():
    '''
    Test that we can count activities in a day
    '''
    day = DayPlan(date=date(2025, 1, 1))
    
    assert len(day.activities) == 0
    
    day.add_activity(Activity("Museum", "museum", 2.0, 20.0, (21.4, 32.4), "Test"))
    assert len(day.activities) == 1
    
    day.add_activity(Activity("Park", "nature", 1.0, 0.0, (21.4, 32.4), "Test"))
    assert len(day.activities) == 2



