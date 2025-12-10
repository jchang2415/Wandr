# Unit Tests for User Preferences Class

import pytest
from models.preferences import UserPreferences

def test_preferences_initialization():
    '''
    Testing initialization of a User Preferences class object and attributes
    '''
    prefs = UserPreferences(
        interests=["museum"],
        budget=300,
        schedule_type="balanced"
    )

    assert prefs.interests == ["museum"]
    assert prefs.budget == 300
    assert prefs.schedule_type == "balanced"
    

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
    assert prefs.include_opening_hours is False


def test_preferences_with_custom_hours():
    '''
    Test preferences with custom hour limits
    '''
    prefs = UserPreferences(
        interests=["museum"],
        budget=500,
        schedule_type="relaxed",
        min_hours_per_day=2.0,
        max_hours_per_day=5.0
    )

    assert prefs.min_hours_per_day == 2.0
    assert prefs.max_hours_per_day == 5.0


def test_preferences_relaxed_schedule():
    '''
    Test relaxed schedule type
    '''
    prefs = UserPreferences(
        interests=["nature"],
        budget=400,
        schedule_type="relaxed"
    )

    assert prefs.schedule_type == "relaxed"


def test_preferences_packed_schedule():
    '''
    Test packed schedule type
    '''
    prefs = UserPreferences(
        interests=["museum", "food", "shopping"],
        budget=1000,
        schedule_type="packed"
    )

    assert prefs.schedule_type == "packed"


def test_preferences_balanced_schedule():
    '''
    Test balanced schedule type
    '''
    prefs = UserPreferences(
        interests=["museum", "food"],
        budget=600,
        schedule_type="balanced"
    )

    assert prefs.schedule_type == "balanced"


def test_preferences_prioritize_cost():
    '''
    Test with cost prioritization enabled
    '''
    prefs = UserPreferences(
        interests=["museum"],
        budget=200,
        schedule_type="balanced",
        prioritize_cost=True
    )

    assert prefs.prioritize_cost is True


def test_preferences_prioritize_distance():
    '''
    Test with distance prioritization enabled
    '''
    prefs = UserPreferences(
        interests=["museum"],
        budget=500,
        schedule_type="balanced",
        prioritize_distance=True
    )

    assert prefs.prioritize_distance is True


def test_preferences_multiple_interests():
    '''
    Test with multiple interests
    '''
    interests = ["museum", "nature", "food", "shopping"]
    prefs = UserPreferences(
        interests=interests,
        budget=800,
        schedule_type="balanced"
    )

    assert len(prefs.interests) == 4
    assert "museum" in prefs.interests
    assert "nature" in prefs.interests
    assert "food" in prefs.interests
    assert "shopping" in prefs.interests


def test_preferences_single_interest():
    '''
    Test with single interest
    '''
    prefs = UserPreferences(
        interests=["food"],
        budget=300,
        schedule_type="relaxed"
    )

    assert len(prefs.interests) == 1
    assert prefs.interests[0] == "food"


def test_preferences_zero_budget():
    '''
    Test with zero budget (free activities only)
    '''
    prefs = UserPreferences(
        interests=["nature"],
        budget=0,
        schedule_type="relaxed",
        prioritize_cost=True
    )

    assert prefs.budget == 0
    assert prefs.prioritize_cost is True


def test_preferences_large_budget():
    '''
    Test with large budget
    '''
    prefs = UserPreferences(
        interests=["museum", "food", "entertainment"],
        budget=5000,
        schedule_type="packed"
    )

    assert prefs.budget == 5000


def test_preferences_with_all_flags_enabled():
    '''
    Test with all optional flags enabled
    '''
    prefs = UserPreferences(
        interests=["museum"],
        budget=500,
        schedule_type="balanced",
        prioritize_cost=True,
        prioritize_distance=True,
        include_opening_hours=True
    )

    assert prefs.prioritize_cost is True
    assert prefs.prioritize_distance is True
    assert prefs.include_opening_hours is True


def test_preferences_fractional_hours():
    '''
    Test with fractional hour limits
    '''
    prefs = UserPreferences(
        interests=["museum"],
        budget=300,
        schedule_type="relaxed",
        min_hours_per_day=2.5,
        max_hours_per_day=6.5
    )

    assert prefs.min_hours_per_day == 2.5
    assert prefs.max_hours_per_day == 6.5


def test_preferences_extreme_hours():
    '''
    Test with extreme hour values
    '''
    prefs = UserPreferences(
        interests=["museum"],
        budget=500,
        schedule_type="packed",
        min_hours_per_day=1.0,
        max_hours_per_day=12.0
    )

    assert prefs.min_hours_per_day == 1.0
    assert prefs.max_hours_per_day == 12.0


def test_preferences_budget_vs_cost_priority():
    '''
    Test relationship between budget and cost priority
    '''
    low_budget_prefs = UserPreferences(
        interests=["museum"],
        budget=100,
        schedule_type="relaxed",
        prioritize_cost=True
    )

    high_budget_prefs = UserPreferences(
        interests=["museum"],
        budget=1000,
        schedule_type="balanced",
        prioritize_cost=False
    )

    assert low_budget_prefs.budget < high_budget_prefs.budget
    assert low_budget_prefs.prioritize_cost is True
    assert high_budget_prefs.prioritize_cost is False


def test_preferences_schedule_type_variations():
    '''
    Test that all schedule types are valid strings
    '''
    for schedule in ["relaxed", "balanced", "packed"]:
        prefs = UserPreferences(
            interests=["museum"],
            budget=500,
            schedule_type=schedule
        )
        assert prefs.schedule_type == schedule


def test_preferences_empty_interests():
    '''
    Test with empty interests list
    '''
    prefs = UserPreferences(
        interests=[],
        budget=500,
        schedule_type="balanced"
    )

    assert prefs.interests == []
    assert len(prefs.interests) == 0


def test_preferences_case_sensitive_interests():
    '''
    Test that interest categories preserve case
    '''
    prefs = UserPreferences(
        interests=["Museum", "FOOD", "nature"],
        budget=500,
        schedule_type="balanced"
    )

    assert "Museum" in prefs.interests
    assert "FOOD" in prefs.interests
    assert "nature" in prefs.interests

