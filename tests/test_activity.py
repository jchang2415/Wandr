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