# Unit Tests for User Preferences Class

from models.preferences import UserPreferences

def test_preferences_defaults():
    '''
    Testing initialization of a User Preferences class object and attributes
    '''
    # Initialize test UserPreferences class object
    prefs = UserPreferences(
        interests=["museum"],
        budget=300,
        schedule_type="balanced"
    )

    # Check default values for attributes
    assert prefs.min_hours_per_day == 3.0
    assert prefs.max_hours_per_day == 8.0
    assert prefs.prioritize_cost is False
    assert prefs.prioritize_distance is False
