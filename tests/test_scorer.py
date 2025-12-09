# Unit Tests for Scoring Engine

from models.activity import Activity
from models.preferences import UserPreferences
from planner.scorer import score_activity

def test_interest_boost():
    '''
    Testing that positive factors for scoring are scored correctly
    '''
    # Initialize test activity
    a = Activity("Art Museum", "museum", 2.0, 15.0)

    # Initialize test User Preferences
    prefs = UserPreferences(
        interests=["museum"],
        budget=300,
        schedule_type="balanced"
    )

    # Use score_activity to generate a score
    score = score_activity(a, prefs)

    # Check that score was increased for an activity matching preferences
    assert score > 20 

def test_cost_penalty():
    '''
    Testing that scorer correctly penalizes costly activities
    '''
    # Initialize test activities
    cheap = Activity("Park", "nature", 1.0, 0.0)
    expensive = Activity("Helicopter Tour", "tour", 2.0, 300.0)

    # Initialize test user preferences
    prefs = UserPreferences(
        interests=["tour"],
        budget=500,
        schedule_type="packed",
        prioritize_cost=True
    )

    # Check that expensive activity is scored lower as expected
    assert score_activity(cheap, prefs) > score_activity(expensive, prefs)

def test_schedule_type_effect():
    '''
    Testing that schedule type preferences affect scoring correctly
    '''
    # Initialize test short activity
    short = Activity("Quick Snack", "food", 0.5, 10.0)

    # Initialize test long activity
    long = Activity("Museum", "museum", 3.0, 30.0)

    # Initialize test user preferences
    relaxed = UserPreferences(["food"], 200, "relaxed")
    packed = UserPreferences(["museum"], 200, "packed")

    # Check that activities that match preferences are scored higher
    assert score_activity(short, relaxed) > score_activity(long, relaxed)
    assert score_activity(long, packed) > score_activity(short, packed)