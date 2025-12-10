# Unit Testing for DayPlan 

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
    a = Activity("Zoo", "nature", 3.0, 15.0)

    # Attempt to use add_activity method of DayPlan class object
    day.add_activity(a)

    # Check that activity was added correctly to DayPlan object
    assert len(day.activities) == 1
    assert day.activities[0].name == "Zoo"

def test_dayplan_total_hours():
    '''
    Test that the total_hours() method of DayPlan class objects works.
    '''
    # Initialize test DayPlan class object with two sample activities
    day = DayPlan(date=date(2025, 1, 1))
    day.add_activity(Activity("Museum", "museum", 2.0, 20.0))
    day.add_activity(Activity("Park", "nature", 1.0, 0.0))

    # Check output of total_hours() method is as expected

    assert day.total_hours() == 3.0
