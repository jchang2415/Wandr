# Scoring Algorithm
'''
Algorithm for scoring each activity based on indicated user preferences.
Takes in an Activity class object and a Preferences class object and outputs a numerical score for the activity.
'''

from models.activity import Activity
from models.preferences import UserPreferences

def score_activity(activity: Activity, prefs: UserPreferences) -> float:
    """
    Compute a score for an activity using:
    - user interests
    - cost preference
    - schedule type
    """

    score = 0.0

    # 1. Interest category match (primary factor)
    if activity.category.lower() in [i.lower() for i in prefs.interests]:
        score += 30

    # 2. Cost sensitivity
    if prefs.prioritize_cost:
        # cheaper activities score higher
        score -= activity.price * 0.5
    else:
        # mild penalty so expensive activities don't dominate
        score -= activity.price * 0.1

    # 3. Scheduler type preferences
    if prefs.schedule_type == "relaxed":
        if activity.duration <= 2:
            score += 10
    elif prefs.schedule_type == "packed":
        if activity.duration >= 2:
            score += 10
    else:
        # balanced mode: no adjustments
        pass

    # 4. A small boost for shorter activities (more flexible)
    score += max(0, 5 - activity.duration)

    return score
