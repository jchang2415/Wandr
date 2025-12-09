# Itinerary Builder

from datetime import timedelta
from typing import List
from models.activity import Activity
from models.trip import Trip
from models.preferences import UserPreferences
from models.itinerary import DayPlan
from planner.scorer import score_activity

def create_itinerary(
    trip: Trip,
    activities: List[Activity],
    prefs: UserPreferences
) -> List[DayPlan]:
    """
    Scheduler that builds an itinerary based on calculated scores and provided information.
    - Computes a score for each activity
    - Sorts them best to worst
    - Fills each day within hour limits
    """

    # Score all available activities based on input
    scored_activities = [(score_activity(a, prefs), a) for a in activities]
    scored_activities.sort(reverse=True, key=lambda x: x[0])

    # Prepare iteration over days
    itinerary = []
    current_date = trip.start_date
    day_index = 0
    remaining_budget = trip.budget

    # Flatten the list to just activities in score order
    sorted_activities = [a for (_, a) in scored_activities]

    # Initialize a set to track which activities have already been used
    used = set()

    while current_date <= trip.end_date:
        day = DayPlan(date=current_date)
        hours_left = prefs.max_hours_per_day

        for activity in sorted_activities:
            if activity in used:
                continue

            # # Check that trip is not over budget
            # if remaining_budget - activity.price < 0:
            #     continue

            # Check time limit
            if activity.duration_hours <= hours_left:

                # Add activity
                day.add_activity(activity)
                used.add(activity)
                hours_left -= activity.duration_hours
                remaining_budget -= activity.price

        itinerary.append(day)
        current_date += timedelta(days=1)

    return itinerary
