# Unit Tests for Scheduling Engine

import pytest
from datetime import date, timedelta
from models.activity import Activity
from models.trip import Trip
from models.preferences import UserPreferences
from engine.scheduler import (
    create_itinerary,
    get_activity_clusters,
    estimate_travel_time
)


# ============================================================================
# FIXTURES - Reusable test data
# ============================================================================

@pytest.fixture
def sample_activities():
    '''
    Sample activities with varied properties
    '''
    return [
        Activity("Museum A", "museum", 2.0, 20.0, (40.7128, -74.0060), "Art museum"),
        Activity("Museum B", "museum", 3.0, 25.0, (40.7200, -74.0100), "History museum"),
        Activity("Park", "nature", 1.0, 0.0, (40.7580, -73.9855), "City park"),
        Activity("Restaurant", "food", 1.5, 30.0, (40.7489, -73.9680), "Fine dining"),
        Activity("Tour", "tour", 2.0, 40.0, (40.7614, -73.9776), "City tour"),
        Activity("Shopping", "shopping", 2.5, 50.0, (40.7589, -73.9787), "Shopping district"),
        Activity("Theater", "entertainment", 3.0, 100.0, (40.7590, -73.9845), "Broadway show"),
        Activity("Free Walk", "nature", 1.5, 0.0, (40.7061, -73.9969), "Historic walk"),
    ]


@pytest.fixture
def sample_activities_no_location():
    '''
    Activities without location data
    '''
    return [
        Activity("Museum", "museum", 2.0, 20.0, None, "Museum"),
        Activity("Park", "nature", 1.0, 0.0, None, "Park"),
        Activity("Restaurant", "food", 1.5, 30.0, None, "Restaurant"),
    ]


@pytest.fixture
def basic_trip():
    '''
    Simple 3-day trip
    '''
    return Trip(
        destination="New York",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 3),
        budget=500,
        interests=["museum", "food"]
    )


@pytest.fixture
def single_day_trip():
    '''
    Single day trip
    '''
    return Trip(
        destination="City",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 1),
        budget=100,
        interests=["museum"]
    )


@pytest.fixture
def balanced_prefs():
    '''
    Balanced schedule preferences
    '''
    return UserPreferences(
        interests=["museum", "food"],
        budget=500,
        schedule_type="balanced",
        max_hours_per_day=8.0
    )


@pytest.fixture
def relaxed_prefs():
    '''
    Relaxed schedule preferences
    '''
    return UserPreferences(
        interests=["nature"],
        budget=200,
        schedule_type="relaxed",
        max_hours_per_day=5.0
    )


@pytest.fixture
def packed_prefs():
    '''
    Packed schedule preferences
    '''
    return UserPreferences(
        interests=["museum", "food", "shopping"],
        budget=1000,
        schedule_type="packed",
        max_hours_per_day=10.0
    )


# ============================================================================
# BASIC SCHEDULER TESTS
# ============================================================================

def test_scheduler_creates_correct_number_of_days(basic_trip, sample_activities, balanced_prefs):
    '''
    Test that scheduler creates one DayPlan per trip day
    '''
    itinerary = create_itinerary(basic_trip, sample_activities, balanced_prefs)
    
    assert len(itinerary) == basic_trip.trip_length()
    assert len(itinerary) == 3


def test_scheduler_respects_daily_hour_limit(basic_trip, sample_activities, balanced_prefs):
    '''
    Test that no day exceeds max_hours_per_day
    '''
    itinerary = create_itinerary(basic_trip, sample_activities, balanced_prefs)
    
    for day in itinerary:
        assert day.total_duration() <= balanced_prefs.max_hours_per_day


def test_scheduler_no_duplicate_activities(basic_trip, sample_activities, balanced_prefs):
    '''
    Test that activities aren't scheduled multiple times
    '''
    itinerary = create_itinerary(basic_trip, sample_activities, balanced_prefs)
    
    seen = set()
    for day in itinerary:
        for activity in day.activities:
            assert activity not in seen, f"Activity '{activity.name}' scheduled twice"
            seen.add(activity)


def test_scheduler_respects_budget(basic_trip, sample_activities):
    '''
    Test that total cost doesn't exceed budget
    '''
    prefs = UserPreferences(
        interests=["museum"],
        budget=50,  # Low budget
        schedule_type="balanced",
        prioritize_cost=True
    )
    
    itinerary = create_itinerary(basic_trip, sample_activities, prefs)
    
    total_cost = sum(day.total_cost() for day in itinerary)
    assert total_cost <= basic_trip.budget


def test_scheduler_with_single_day_trip(single_day_trip, sample_activities, balanced_prefs):
    '''
    Test scheduler with one-day trip
    '''
    itinerary = create_itinerary(single_day_trip, sample_activities, balanced_prefs)
    
    assert len(itinerary) == 1
    assert itinerary[0].date == single_day_trip.start_date


def test_scheduler_with_no_activities(basic_trip, balanced_prefs):
    '''
    Test scheduler with empty activity list
    '''
    itinerary = create_itinerary(basic_trip, [], balanced_prefs)
    
    assert len(itinerary) == basic_trip.trip_length()
    for day in itinerary:
        assert len(day.activities) == 0


def test_scheduler_with_single_activity(basic_trip, balanced_prefs):
    '''
    Test scheduler with only one activity available
    '''
    activities = [Activity("Museum", "museum", 2.0, 20.0, (40.7128, -74.0060), "Museum")]
    
    itinerary = create_itinerary(basic_trip, activities, balanced_prefs)
    
    # Should only appear once across all days
    total_activities = sum(len(day.activities) for day in itinerary)
    assert total_activities == 1


# ============================================================================
# SCHEDULE TYPE TESTS
# ============================================================================

def test_scheduler_relaxed_has_fewer_activities(basic_trip, sample_activities, relaxed_prefs):
    '''
    Test that relaxed schedule has fewer activities per day
    '''
    itinerary = create_itinerary(basic_trip, sample_activities, relaxed_prefs)
    
    for day in itinerary:
        # Relaxed should have shorter days
        assert day.total_duration() <= 5.0
        # Typically fewer activities
        assert len(day.activities) <= 4


def test_scheduler_packed_maximizes_activities(basic_trip, sample_activities, packed_prefs):
    '''
    Test that packed schedule tries to fit more activities
    '''
    relaxed_prefs = UserPreferences(
        interests=["museum", "food", "shopping"],
        budget=1000,
        schedule_type="relaxed",
        max_hours_per_day=5.0
    )
    
    packed_itinerary = create_itinerary(basic_trip, sample_activities, packed_prefs)
    relaxed_itinerary = create_itinerary(basic_trip, sample_activities, relaxed_prefs)
    
    packed_total = sum(len(day.activities) for day in packed_itinerary)
    relaxed_total = sum(len(day.activities) for day in relaxed_itinerary)
    
    # Packed should schedule more activities overall
    assert packed_total >= relaxed_total


# ============================================================================
# GEOGRAPHIC CLUSTERING TESTS
# ============================================================================

def test_scheduler_groups_nearby_activities(basic_trip, sample_activities, balanced_prefs):
    '''
    Test that scheduler tends to group geographically close activities
    '''
    balanced_prefs.prioritize_distance = True
    itinerary = create_itinerary(basic_trip, sample_activities, balanced_prefs)
    
    # Check that activities on same day are relatively close
    for day in itinerary:
        if len(day.activities) >= 2:
            locations = [a.location for a in day.activities if a.location]
            if len(locations) >= 2:
                # Calculate average distance between consecutive activities
                from utils.haversine import haversine_distance_km
                distances = []
                for i in range(len(locations) - 1):
                    dist = haversine_distance_km(locations[i], locations[i+1])
                    distances.append(dist)
                avg_distance = sum(distances) / len(distances)
                
                # Activities should generally be within 5km of each other
                assert avg_distance < 5.0


def test_scheduler_without_locations(basic_trip, sample_activities_no_location, balanced_prefs):
    '''
    Test that scheduler works when activities have no location data
    '''
    itinerary = create_itinerary(basic_trip, sample_activities_no_location, balanced_prefs)
    
    # Should still create valid itinerary
    assert len(itinerary) == basic_trip.trip_length()
    # Should have some activities scheduled
    total_activities = sum(len(day.activities) for day in itinerary)
    assert total_activities > 0


# ============================================================================
# LOCKED ACTIVITIES TESTS
# ============================================================================

def test_scheduler_respects_locked_activities(basic_trip, sample_activities, balanced_prefs):
    '''
    Test that locked activities appear in itinerary
    '''
    museum = sample_activities[0]
    park = sample_activities[2]
    locked = [museum, park]
    
    itinerary = create_itinerary(basic_trip, sample_activities, balanced_prefs, locked_activities=locked)
    
    # Check that both locked activities appear
    all_scheduled = []
    for day in itinerary:
        all_scheduled.extend(day.activities)
    
    assert museum in all_scheduled, "Locked museum not in itinerary"
    assert park in all_scheduled, "Locked park not in itinerary"


def test_scheduler_prioritizes_locked_activities(basic_trip, sample_activities):
    '''
    Test that locked activities are scheduled first
    '''
    expensive_activity = Activity("Expensive Tour", "tour", 8.0, 200.0, (40.7128, -74.0060), "Tour")
    all_activities = sample_activities + [expensive_activity]
    
    prefs = UserPreferences(
        interests=["tour"],
        budget=250,
        schedule_type="balanced",
        max_hours_per_day=9.0
    )
    
    itinerary = create_itinerary(basic_trip, all_activities, prefs, locked_activities=[expensive_activity])
    
    # Expensive activity should appear despite budget constraints
    all_scheduled = []
    for day in itinerary:
        all_scheduled.extend(day.activities)
    
    assert expensive_activity in all_scheduled


# ============================================================================
# INTEREST MATCHING TESTS
# ============================================================================

def test_scheduler_prioritizes_user_interests(basic_trip, sample_activities):
    '''
    Test that activities matching interests are prioritized
    '''
    museum_prefs = UserPreferences(
        interests=["museum"],
        budget=500,
        schedule_type="balanced"
    )
    
    itinerary = create_itinerary(basic_trip, sample_activities, museum_prefs)
    
    # Count museum activities scheduled
    museum_count = 0
    for day in itinerary:
        for activity in day.activities:
            if activity.category == "museum":
                museum_count += 1
    
    # Should have at least one museum activity
    assert museum_count >= 1


def test_scheduler_with_no_matching_interests(basic_trip, sample_activities):
    '''
    Test scheduler when no activities match user interests
    '''
    prefs = UserPreferences(
        interests=["scuba_diving"],  # Not in sample activities
        budget=500,
        schedule_type="balanced"
    )
    
    itinerary = create_itinerary(basic_trip, sample_activities, prefs)
    
    # Should still schedule some activities
    total_activities = sum(len(day.activities) for day in itinerary)
    assert total_activities > 0

# ============================================================================
# EDGE CASES
# ============================================================================

def test_scheduler_with_very_long_trip():
    '''
    Test scheduler with extended trip duration
    '''
    long_trip = Trip(
        destination="City",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 14),  # 14 days
        budget=2000,
        interests=["museum"]
    )
    
    activities = [
        Activity(f"Activity {i}", "museum", 2.0, 20.0, None, f"Activity {i}")
        for i in range(50)  # Many activities
    ]
    
    prefs = UserPreferences(
        interests=["museum"],
        budget=2000,
        schedule_type="balanced"
    )
    
    itinerary = create_itinerary(long_trip, activities, prefs)
    
    assert len(itinerary) == 14


def test_scheduler_with_all_expensive_activities(basic_trip):
    '''
    Test when all activities exceed budget
    '''
    expensive_activities = [
        Activity(f"Expensive {i}", "tour", 2.0, 200.0, None, "Tour")
        for i in range(5)
    ]
    
    prefs = UserPreferences(
        interests=["tour"],
        budget=100,  # Can't afford any
        schedule_type="balanced"
    )
    
    itinerary = create_itinerary(basic_trip, expensive_activities, prefs)
    
    # Should create itinerary structure even if empty
    assert len(itinerary) == basic_trip.trip_length()


def test_scheduler_with_activities_too_long(single_day_trip, balanced_prefs):
    '''
    Test when activities are longer than available time
    '''
    long_activities = [
        Activity("Long Activity", "museum", 10.0, 20.0, None, "Too long")
    ]
    
    balanced_prefs.max_hours_per_day = 5.0
    
    itinerary = create_itinerary(single_day_trip, long_activities, balanced_prefs)
    
    # Activity shouldn't be scheduled
    assert len(itinerary[0].activities) == 0


# ============================================================================
# UTILITY FUNCTION TESTS
# ============================================================================

def test_get_activity_clusters(sample_activities):
    '''
    Test geographic clustering of activities
    '''
    clusters = get_activity_clusters(sample_activities, max_distance_km=2.0)
    
    # Should find some clusters
    assert len(clusters) >= 1
    
    # Each cluster should have multiple activities
    for cluster in clusters:
        assert len(cluster) >= 2


def test_get_activity_clusters_no_locations():
    '''
    Test clustering with activities without locations
    '''
    activities = [
        Activity("A", "museum", 2.0, 20.0, None, "A"),
        Activity("B", "museum", 2.0, 20.0, None, "B"),
    ]
    
    clusters = get_activity_clusters(activities)
    
    # Should return empty or handle gracefully
    assert isinstance(clusters, list)


def test_estimate_travel_time():
    '''
    Test travel time estimation
    '''
    loc1 = (40.7128, -74.0060)  # NYC
    loc2 = (40.7580, -73.9855)  # Times Square
    
    activity1 = Activity("A", "museum", 2.0, 20.0, loc1, "A")
    activity2 = Activity("B", "landmark", 2.0, 20.0, loc2, "B")
    
    travel_time = estimate_travel_time(activity1, activity2)
    
    # Should be positive
    assert travel_time > 0
    # Should include buffer time (at least 0.25 hours)
    assert travel_time >= 0.25


def test_estimate_travel_time_no_locations():
    '''
    Test travel time when locations are missing
    '''
    activity1 = Activity("A", "museum", 2.0, 20.0, None, "A")
    activity2 = Activity("B", "museum", 2.0, 20.0, None, "B")
    
    travel_time = estimate_travel_time(activity1, activity2)
    
    # Should return default time
    assert travel_time == 0.25


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_full_itinerary_generation_workflow(sample_activities):
    '''
    Test overall full itinerary generation workflow
    '''
    trip = Trip(
        destination="New York",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 5),
        budget=800,
        interests=["museum", "food", "nature"]
    )
    
    prefs = UserPreferences(
        interests=["museum", "food", "nature"],
        budget=800,
        schedule_type="balanced",
        prioritize_distance=True
    )
    
    itinerary = create_itinerary(trip, sample_activities, prefs)
    
    # Verify basic structure
    assert len(itinerary) == 5
    
    # Verify no day is overbooked
    for day in itinerary:
        assert day.total_duration() <= prefs.max_hours_per_day
    
    # Verify budget
    total_cost = sum(day.total_cost() for day in itinerary)
    assert total_cost <= trip.budget
    
    # Verify no duplicates
    all_activities = []
    for day in itinerary:
        all_activities.extend(day.activities)
    assert len(all_activities) == len(set(all_activities))


def test_itinerary_dates_match_trip_dates(basic_trip, sample_activities, balanced_prefs):
    '''
    Test that each day in itinerary has correct date
    '''
    itinerary = create_itinerary(basic_trip, sample_activities, balanced_prefs)
    
    expected_date = basic_trip.start_date
    for day in itinerary:
        assert day.date == expected_date
        expected_date += timedelta(days=1)
    
    assert expected_date == basic_trip.end_date + timedelta(days=1)


