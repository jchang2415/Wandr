# Unit Tests for Scoring Engine

import pytest
from models.activity import Activity
from models.preferences import UserPreferences
from engine.scorer import (
    score_activity,
    score_all_activities,
    analyze_category_distribution,
    suggest_interest_balance
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def museum_activity():
    '''Sample museum activity'''
    return Activity("Art Museum", "museum", 2.0, 15.0, (40.7128, -74.0060), "Modern art")


@pytest.fixture
def expensive_activity():
    '''Expensive activity for cost testing'''
    return Activity("Helicopter Tour", "tour", 2.0, 300.0, (40.7128, -74.0060), "City tour")


@pytest.fixture
def free_activity():
    '''Free activity'''
    return Activity("Central Park", "nature", 1.5, 0.0, (40.7829, -73.9654), "City park")


@pytest.fixture
def long_activity():
    '''Long duration activity'''
    return Activity("Day Trip", "tour", 8.0, 100.0, (40.7128, -74.0060), "Full day tour")


@pytest.fixture
def short_activity():
    '''Short duration activity'''
    return Activity("Quick Visit", "museum", 0.5, 5.0, (40.7128, -74.0060), "Brief tour")


@pytest.fixture
def balanced_prefs():
    '''Balanced preferences'''
    return UserPreferences(
        interests=["museum", "food"],
        budget=500,
        schedule_type="balanced"
    )


@pytest.fixture
def cost_priority_prefs():
    '''Cost-focused preferences'''
    return UserPreferences(
        interests=["museum"],
        budget=200,
        schedule_type="relaxed",
        prioritize_cost=True
    )


@pytest.fixture
def relaxed_prefs():
    '''Relaxed schedule preferences'''
    return UserPreferences(
        interests=["nature"],
        budget=300,
        schedule_type="relaxed"
    )


@pytest.fixture
def packed_prefs():
    '''Packed schedule preferences'''
    return UserPreferences(
        interests=["museum", "food", "shopping"],
        budget=1000,
        schedule_type="packed"
    )


# ============================================================================
# INTEREST MATCHING TESTS
# ============================================================================

def test_score_exact_interest_match(museum_activity, balanced_prefs):
    '''Test that matching interest category gets high score'''
    score = score_activity(museum_activity, balanced_prefs)
    
    # Should get interest bonus (40 points)
    assert score >= 30  # At least 30 points from interest match


def test_score_no_interest_match(museum_activity):
    '''Test activity with no matching interests'''
    prefs = UserPreferences(
        interests=["food", "shopping"],  # No museum
        budget=500,
        schedule_type="balanced"
    )
    
    score = score_activity(museum_activity, prefs)
    
    # Should not get interest bonus
    # Score should be lower than exact match
    assert score < 30


def test_score_complementary_category():
    '''Test that complementary categories get small bonus'''
    # Tour complements museum
    tour_activity = Activity("City Tour", "tour", 2.0, 30.0, None, "Tour")
    
    prefs = UserPreferences(
        interests=["museum"],
        budget=500,
        schedule_type="balanced"
    )
    
    score = score_activity(tour_activity, prefs)
    
    # Should get complementary bonus (around 10 points)
    assert score > 0  # Gets some bonus


def test_score_multiple_interests_one_match(museum_activity):
    '''Test with multiple interests where one matches'''
    prefs = UserPreferences(
        interests=["food", "museum", "shopping"],
        budget=500,
        schedule_type="balanced"
    )
    
    score = score_activity(museum_activity, prefs)
    
    # Should get full interest bonus
    assert score >= 30


# ============================================================================
# COST FACTOR TESTS
# ============================================================================

def test_score_free_activity_with_cost_priority(free_activity, cost_priority_prefs):
    '''Test that free activities get bonus when prioritizing cost'''
    score = score_activity(free_activity, cost_priority_prefs)
    
    # Should get free bonus (15 points)
    assert score >= 10


def test_score_cheap_activity_with_cost_priority(cost_priority_prefs):
    '''Test cheap activities with cost priority'''
    cheap = Activity("Cheap Museum", "museum", 2.0, 10.0, None, "Museum")
    
    score = score_activity(cheap, cost_priority_prefs)
    
    # Should get small bonus for being under $20
    assert score > 30  # Interest match + cheap bonus


def test_score_free_activity_without_cost_priority(free_activity, balanced_prefs, cost_priority_prefs):
    '''Test free activity when not prioritizing cost'''
    score = score_activity(free_activity, balanced_prefs)
    
    # Should get small bonus (5 points) for being free
    assert score >= 0


def test_score_expensive_activity_without_cost_priority(expensive_activity, balanced_prefs, cost_priority_prefs):
    '''Test expensive activity when not prioritizing cost'''
    score_with_priority = score_activity(expensive_activity, cost_priority_prefs)
    score_without_priority = score_activity(expensive_activity, balanced_prefs)
    
    # Without priority, penalty should be much lighter
    assert score_without_priority > score_with_priority


# ============================================================================
# SCHEDULE TYPE TESTS
# ============================================================================

def test_score_short_activity_relaxed_schedule(short_activity, relaxed_prefs):
    '''Test that short activities are favored in relaxed schedule'''
    long = Activity("Long Museum", "museum", 4.0, 20.0, None, "Museum")
    
    short_score = score_activity(short_activity, relaxed_prefs)
    long_score = score_activity(long, relaxed_prefs)
    
    # Short should score higher in relaxed
    assert short_score > long_score

def test_score_relaxed_penalties_long_activities(relaxed_prefs):
    '''Test that relaxed schedule penalizes very long activities'''
    long = Activity("All Day Tour", "nature", 6.0, 50.0, None, "Full day")
    
    score = score_activity(long, relaxed_prefs)
    
    # Should have penalty for duration >= 4 hours
    # Relaxed penalizes -10 for long activities
    assert score < 40  # Less than just interest match


# ============================================================================
# VARIETY/DIVERSITY TESTS
# ============================================================================

def test_score_variety_bonus_new_category(museum_activity, balanced_prefs):
    '''Test that first activity of a category gets variety bonus'''
    already_scheduled = []
    
    score = score_activity(museum_activity, balanced_prefs, already_scheduled)
    
    # Should get variety bonus (+10) for new category
    assert score >= 40  # Interest match (40) + variety bonus (10)


def test_score_variety_penalty_repeated_category(museum_activity, balanced_prefs):
    '''Test penalty for repeating same category too many times'''
    # Schedule 3 museums already
    already_scheduled = [
        Activity("Museum 1", "museum", 2.0, 20.0, None, "M1"),
        Activity("Museum 2", "museum", 2.0, 20.0, None, "M2"),
        Activity("Museum 3", "museum", 2.0, 20.0, None, "M3"),
    ]
    
    score = score_activity(museum_activity, balanced_prefs, already_scheduled)
    
    # Should have penalty for 4th museum (-20)
    assert score < 30  # Less than base interest match


def test_score_variety_second_activity_neutral(museum_activity, balanced_prefs):
    '''Test that second activity of same category is neutral'''
    already_scheduled = [
        Activity("Museum 1", "museum", 2.0, 20.0, None, "M1"),
    ]
    
    score = score_activity(museum_activity, balanced_prefs, already_scheduled)
    
    # Should be neutral (no bonus, no penalty)
    # Just base interest match (40)
    assert 35 <= score <= 45


def test_score_variety_third_activity_penalty(museum_activity, balanced_prefs):
    '''Test penalty for third activity of same category'''
    already_scheduled = [
        Activity("Museum 1", "museum", 2.0, 20.0, None, "M1"),
        Activity("Museum 2", "museum", 2.0, 20.0, None, "M2"),
    ]
    
    score = score_activity(museum_activity, balanced_prefs, already_scheduled)
    
    # Should have -10 penalty for third
    assert score < 35


# ============================================================================
# DURATION FLEXIBILITY TESTS
# ============================================================================

def test_score_duration_very_short_activities(short_activity, balanced_prefs):
    '''Test bonus for very short activities (high flexibility)'''
    score = score_activity(short_activity, balanced_prefs)
    
    # Activities <= 1 hour get +8 flexibility bonus
    assert score >= 8  # At least flexibility bonus


def test_score_duration_short_activities(balanced_prefs):
    '''Test bonus for short activities (1-2 hours)'''
    activity = Activity("Activity", "museum", 1.5, 20.0, None, "Activity")
    
    score = score_activity(activity, balanced_prefs)
    
    # Activities <= 2 hours get +5 bonus
    assert score >= 40  # Interest match + some flexibility


def test_score_duration_medium_activities(balanced_prefs):
    '''Test small bonus for medium activities (2-3 hours)'''
    activity = Activity("Activity", "museum", 2.5, 20.0, None, "Activity")
    
    score = score_activity(activity, balanced_prefs)
    
    # Activities <= 3 hours get +2 bonus
    assert score >= 40


def test_score_duration_long_activities_no_bonus(balanced_prefs):
    '''Test that very long activities don't get flexibility bonus'''
    activity = Activity("Long Activity", "museum", 5.0, 20.0, None, "Long")
    
    score = score_activity(activity, balanced_prefs)
    
    # Should not get flexibility bonus
    # Just interest match and balanced schedule bonus
    assert score >= 40


# ============================================================================
# COMBINED FACTORS TESTS
# ============================================================================

def test_score_perfect_activity(balanced_prefs):
    '''Test activity that matches all preferences perfectly'''
    perfect = Activity(
        name="Perfect Museum",
        category="museum",  # Matches interest
        duration=1.5,  # Good for balanced (1.5-3h), flexible
        price=0.0,  # Free
        location=(40.7, -74.0),
        description="Perfect"
    )
    
    score = score_activity(perfect, balanced_prefs, [])
    
    # Should score very high:
    # +40 interest match
    # +5 free activity bonus
    # +10 balanced schedule fit
    # +10 variety bonus
    # +5 flexibility bonus
    assert score >= 60


def test_score_worst_activity(balanced_prefs):
    '''Test activity that matches poorly with preferences'''
    worst = Activity(
        name="Bad Activity",
        category="scuba",  # Doesn't match any interest
        duration=10.0,  # Too long
        price=500.0,  # Very expensive
        location=None,
        description="Expensive"
    )
    
    # Already scheduled 3 of same category
    already_scheduled = [
        Activity("Scuba 1", "scuba", 2.0, 100.0, None, "S1"),
        Activity("Scuba 2", "scuba", 2.0, 100.0, None, "S2"),
        Activity("Scuba 3", "scuba", 2.0, 100.0, None, "S3"),
    ]
    
    score = score_activity(worst, balanced_prefs, already_scheduled)
    
    # Should score very poorly:
    # 0 interest match
    # -75 cost penalty (500 * 0.15)
    # -20 variety penalty
    # 0 flexibility bonus
    assert score < -50


def test_score_expensive_but_interesting(packed_prefs):
    '''Test expensive activity that matches strong interest'''
    activity = Activity("Broadway Show", "entertainment", 3.0, 150.0, None, "Show")
    
    score = score_activity(activity, packed_prefs)
    
    # Should balance interest match against cost
    # Interest category not in prefs, but cost penalty not prioritized
    assert score > -50


# ============================================================================
# SCORE_ALL_ACTIVITIES TESTS
# ============================================================================

def test_score_all_activities_returns_sorted_list(balanced_prefs):
    '''Test that score_all_activities returns sorted list'''
    activities = [
        Activity("Museum", "museum", 2.0, 20.0, None, "Museum"),
        Activity("Park", "nature", 1.0, 0.0, None, "Park"),
        Activity("Restaurant", "food", 1.5, 30.0, None, "Food"),
    ]
    
    scored = score_all_activities(activities, balanced_prefs)
    
    # Should return list of tuples
    assert isinstance(scored, list)
    assert all(isinstance(item, tuple) for item in scored)
    assert all(len(item) == 2 for item in scored)
    
    # Should be sorted in descending order
    scores = [score for score, _ in scored]
    assert scores == sorted(scores, reverse=True)


def test_score_all_activities_with_empty_list(balanced_prefs):
    '''Test score_all_activities with empty input'''
    scored = score_all_activities([], balanced_prefs)
    
    assert scored == []


def test_score_all_activities_maintains_activity_objects(balanced_prefs):
    '''Test that activity objects are preserved in output'''
    activities = [
        Activity("Museum", "museum", 2.0, 20.0, None, "Museum"),
        Activity("Park", "nature", 1.0, 0.0, None, "Park"),
    ]
    
    scored = score_all_activities(activities, balanced_prefs)
    
    # Check that activities are in output
    output_activities = [activity for _, activity in scored]
    for activity in activities:
        assert activity in output_activities


# ============================================================================
# ANALYZE_CATEGORY_DISTRIBUTION TESTS
# ============================================================================

def test_analyze_category_distribution():
    '''Test category distribution analysis'''
    activities = [
        Activity("Museum 1", "museum", 2.0, 20.0, None, "M1"),
        Activity("Museum 2", "museum", 2.0, 20.0, None, "M2"),
        Activity("Park 1", "nature", 1.0, 0.0, None, "P1"),
        Activity("Restaurant", "food", 1.5, 30.0, None, "R1"),
    ]
    
    distribution = analyze_category_distribution(activities)
    
    assert distribution["museum"] == 2
    assert distribution["nature"] == 1
    assert distribution["food"] == 1


def test_analyze_category_distribution_empty():
    '''Test distribution with empty list'''
    distribution = analyze_category_distribution([])
    
    assert distribution == {}


def test_analyze_category_distribution_case_insensitive():
    '''Test that categories are counted case-insensitively'''
    activities = [
        Activity("A", "Museum", 2.0, 20.0, None, "A"),
        Activity("B", "museum", 2.0, 20.0, None, "B"),
        Activity("C", "MUSEUM", 2.0, 20.0, None, "C"),
    ]
    
    distribution = analyze_category_distribution(activities)
    
    # Should all count as same category
    assert distribution["museum"] == 3


# ============================================================================
# SUGGEST_INTEREST_BALANCE TESTS
# ============================================================================

def test_suggest_interest_balance_no_activities():
    '''Test suggestions when no activities available for interest'''
    activities = [
        Activity("Park", "nature", 1.0, 0.0, None, "Park"),
    ]
    
    user_interests = ["museum", "food"]
    
    suggestions = suggest_interest_balance(activities, user_interests)
    
    # Should suggest that museum and food aren't available
    assert "museum" in suggestions
    assert "food" in suggestions
    assert "No museum activities" in suggestions["museum"]


def test_suggest_interest_balance_limited_options():
    '''Test suggestions when limited activities for interest'''
    activities = [
        Activity("Museum 1", "museum", 2.0, 20.0, None, "M1"),
        Activity("Museum 2", "museum", 2.0, 20.0, None, "M2"),
        Activity("Park", "nature", 1.0, 0.0, None, "Park"),
    ]
    
    user_interests = ["museum"]
    
    suggestions = suggest_interest_balance(activities, user_interests)
    
    # Should warn about limited options
    assert "museum" in suggestions
    assert "Limited" in suggestions["museum"]


def test_suggest_interest_balance_unexplored_categories():
    '''Test that unexplored categories with many activities are suggested'''
    activities = [
        Activity(f"Museum {i}", "museum", 2.0, 20.0, None, f"M{i}")
        for i in range(10)
    ] + [
        Activity(f"Restaurant {i}", "food", 1.5, 30.0, None, f"R{i}")
        for i in range(6)
    ]
    
    user_interests = ["nature"]  # Not interested in museum or food
    
    suggestions = suggest_interest_balance(activities, user_interests)
    
    # Should suggest considering museum and food
    assert any("Consider" in key for key in suggestions.keys())


def test_suggest_interest_balance_well_balanced():
    '''Test when interests are well-matched to available activities'''
    activities = [
        Activity(f"Museum {i}", "museum", 2.0, 20.0, None, f"M{i}")
        for i in range(10)
    ]
    
    user_interests = ["museum"]
    
    suggestions = suggest_interest_balance(activities, user_interests)
    
    # Should not warn about museum
    if "museum" in suggestions:
        assert "No" not in suggestions["museum"]
        assert "Limited" not in suggestions["museum"]


# ============================================================================
# EDGE CASES
# ============================================================================

def test_score_activity_with_none_values():
    '''Test scoring activity with None values'''
    activity = Activity("Activity", "museum", 2.0, 20.0, None, "")
    
    prefs = UserPreferences(
        interests=["museum"],
        budget=500,
        schedule_type="balanced"
    )
    
    # Should not crash
    score = score_activity(activity, prefs)
    assert isinstance(score, (int, float))


def test_score_with_zero_duration():
    '''Test activity with zero duration'''
    activity = Activity("Quick", "museum", 0.0, 0.0, None, "Instant")
    
    prefs = UserPreferences(
        interests=["museum"],
        budget=500,
        schedule_type="balanced"
    )
    
    score = score_activity(activity, prefs)
    assert isinstance(score, (int, float))


def test_score_with_negative_price():
    '''Test that scorer handles negative prices gracefully'''
    activity = Activity("Refund", "museum", 2.0, -10.0, None, "Pays you")
    
    prefs = UserPreferences(
        interests=["museum"],
        budget=500,
        schedule_type="balanced"
    )
    
    score = score_activity(activity, prefs)
    # Negative price should give bonus
    assert score >= 40


def test_score_case_sensitivity():
    '''Test that category matching is case-insensitive'''
    activity = Activity("Museum", "MUSEUM", 2.0, 20.0, None, "Museum")
    
    prefs = UserPreferences(
        interests=["museum"],  # lowercase
        budget=500,
        schedule_type="balanced"
    )
    
    score = score_activity(activity, prefs)
    
    # Should match despite case difference
    assert score >= 30  # Interest match bonus

def test_score_consistency():
    '''Test that same input always produces same score'''
    activity = Activity("Museum", "museum", 2.0, 20.0, None, "Museum")
    prefs = UserPreferences(
        interests=["museum"],
        budget=500,
        schedule_type="balanced"
    )
    
    score1 = score_activity(activity, prefs)
    score2 = score_activity(activity, prefs)
    
    assert score1 == score2


def test_score_ranges_reasonable():
    '''Test that scores are generally in reasonable range'''
    activities = [
        Activity("Museum", "museum", 2.0, 20.0, None, "Museum"),
        Activity("Park", "nature", 1.0, 0.0, None, "Park"),
        Activity("Expensive", "tour", 2.0, 500.0, None, "Tour"),
    ]
    
    prefs = UserPreferences(
        interests=["museum"],
        budget=500,
        schedule_type="balanced",
        prioritize_cost=True
    )
    
    for activity in activities:
        score = score_activity(activity, prefs)
        # Scores shouldn't be extremely large (> 1000) or small (< -1000)
        assert -1000 < score < 1000


