# Unit Tests for Scheduling Enginer

from datetime import date
from models.activity import Activity
from models.trip import Trip
from models.preferences import UserPreferences
from engine.scheduler import create_itinerary

# Generate sample Activities data for testing
def sample_data():
    activities = [
        Activity("Museum", "museum", 2.0, 20.0, (21.4, 32.4), "Test"),
        Activity("Zoo", "nature", 3.0, 25.0, (21.4, 32.4), "Test"),
        Activity("Boat Tour", "tour", 1.5, 40.0, (21.4, 32.4), "Test"),
        Activity("Park", "nature", 1.0, 0.0, (21.4, 32.4), "Test")
    ]
    return activities

def test_scheduler_respects_day_limits():
    '''
    Testing that scheduler doesn't overschedule over time limit
    '''
    # Initialize test trip and user preferences
    trip = Trip("Chicago", date(2025,1,1), date(2025,1,2), 500, ["museum"])
    prefs = UserPreferences(["museum"], 500, "balanced", max_hours_per_day=3.0)

    # Use create_itinerary() to generate an activity using scheduler
    itinerary = create_itinerary(trip, sample_data(), prefs)

    # Check that scheduled itineraries are within time limits
    for day in itinerary:
        assert day.total_hours() <= 3.0

def test_scheduler_no_duplicate_activities():
    '''
    Testing that activities aren't double scheduled by scheduling engine
    '''
    # Generate test trip and user preferences
    trip = Trip("Chicago", date(2025,1,1), date(2025,1,2), 500, ["museum"])
    prefs = UserPreferences(["museum"], 500, "balanced")

    # Use scheduler to generate itinerary using test objects
    itinerary = create_itinerary(trip, sample_data(), prefs)

    # Check that activities aren't duplicated during itinerary generation process
    seen = set()
    for day in itinerary:
        for act in day.activities:
            assert act not in seen
            seen.add(act)

def test_scheduler_respects_budget():
    '''
    Testing that scheduler stays within provided budget
    '''
    # Generate test trip object and user preferences
    trip = Trip("Chicago", date(2025,1,1), date(2025,1,1), 30, ["museum"])
    prefs = UserPreferences(["museum"], 30, "balanced")

    # Use scheduler to generate itinerary from test objects
    itinerary = create_itinerary(trip, sample_data(), prefs)

    # Check that total cost of generated itinerary is within specified budget
    day = itinerary[0]
    total_cost = sum(a.price for a in day.activities)

    assert total_cost <= 30

