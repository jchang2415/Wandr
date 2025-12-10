# Unit Tests for Activity Class

import pytest
from models.activity import Activity

def test_activity_initialization():
    '''
    Test to ensure initialization of Activity class objects works and has the desired attributes
    '''
    a = Activity(
        name="Museum",
        category="museum",
        duration_hours=2.0,
        price=20.0,
        location=(41.0, -87.0),
        description="A great museum."
    )

    assert a.name == "Museum"
    assert a.category == "museum"
    assert a.duration_hours == 2.0
    assert a.price == 20.0
    assert a.location == (41.0, -87.0)
    assert a.description == "A great museum."

def test_activity_default_values():
    '''
    Testing default values for Activity class objects.
    '''
    a = Activity("Park", "nature", 1.0, 0.0)

    assert a.location is None

    assert a.description == ""


def test_activity_to_dict():
    '''
    Test that to_dict() method correctly converts Activity to dictionary
    '''
    a = Activity(
        name="Museum",
        category="museum",
        duration_hours=2.5,
        price=20.0,
        location=(41.0, -87.0),
        description="A great museum."
    )
    
    result = a.to_dict()
    
    assert result["name"] == "Museum"
    assert result["category"] == "museum"
    assert result["duration_hours"] == 2.5
    assert result["price"] == 20.0
    assert result["location"] == (41.0, -87.0)
    assert result["description"] == "A great museum."


def test_activity_to_dict_with_none_values():
    '''
    Test that to_dict() handles None values correctly
    '''
    a = Activity("Park", "nature", 1.0, 0.0)
    
    result = a.to_dict()
    
    assert result["location"] is None
    assert result["description"] == ""


def test_activity_equality():
    '''
    Test that two activities with same attributes are equal
    '''
    a1 = Activity("Museum", "museum", 2.0, 20.0, (41.0, -87.0), "Great place")
    a2 = Activity("Museum", "museum", 2.0, 20.0, (41.0, -87.0), "Great place")
    
    assert a1 == a2


def test_activity_inequality():
    '''
    Test that activities with different attributes are not equal
    '''
    a1 = Activity("Museum", "museum", 2.0, 20.0)
    a2 = Activity("Park", "nature", 1.0, 0.0)
    
    assert a1 != a2


def test_activity_with_zero_price():
    '''
    Test that activities can have zero price (free activities)
    '''
    a = Activity("Free Park", "nature", 1.0, 0.0)
    
    assert a.price == 0.0


def test_activity_with_fractional_duration():
    '''
    Test that activities can have fractional hour durations
    '''
    a = Activity("Quick Tour", "tour", 0.5, 10.0)
    
    assert a.duration_hours == 0.5


def test_activity_category_case_sensitivity():
    '''
    Test that category preserves case
    '''
    a = Activity("Museum", "Museum", 2.0, 20.0)
    
    assert a.category == "Museum"  # Case is preserved


def test_activity_with_coordinates():
    '''
    Test that location coordinates are stored correctly
    '''
    a = Activity("Eiffel Tower", "landmark", 2.0, 25.0, (48.8584, 2.2945))
    
    assert a.location[0] == 48.8584  # Latitude
    assert a.location[1] == 2.2945   # Longitude
