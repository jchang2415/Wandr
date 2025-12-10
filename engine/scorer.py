# Scoring Algorithm
'''
Algorithm for scoring each activity based on indicated user preferences.
Takes in an Activity class object and a Preferences class object and outputs a numerical score for the activity.
'''

from models.activity import Activity
from models.preferences import UserPreferences

def score_activity(activity, prefs, already_scheduled = None):
    '''
    Scoring that considers:
    - User interests (primary factor)
    - Cost preferences
    - Schedule type
    - Variety (penalize too many of same category)
    - Duration flexibility
    
    **Parameters**

        activity: *Activity*
            Activity to score

        prefs: *UserPreferences*
            User preferences

        already_scheduled: *list[Activity]*
            Activities already in itinerary (for variety)
    
    Returns:

        score: *float*
            Final score calculated for the activity
    '''
    already_scheduled = already_scheduled or []
    
    # Normalize values
    category = (activity.category or "").lower()
    interests = [i.lower() for i in prefs.interests]
    price = max(activity.price, 0)  # prevent negative price effects
    
    # Initialize score
    score = 0.0
    
    # 1. USER INTEREST MATCH (30-40 points)
    if activity.category.lower() in [i.lower() for i in prefs.interests]:
        score += 40  # Increased from 30
    else:
        # Add small bonus for complementary categories
        complementary = {
            'museum': ['landmark', 'tour'],
            'nature': ['tour'],
            'food': [],  # Food is universal
            'shopping': [],
            'landmark': ['museum', 'tour'],
            'tour': ['museum', 'landmark', 'nature'],
            'entertainment': []
        }
        
        for interest in prefs.interests:
            if activity.category.lower() in complementary.get(interest.lower(), []):
                score += 10
                break
    
    # 2. COST FACTOR (-50 to +10 points)
    
    # If cost is listed as a priority
    if prefs.prioritize_cost:

        # Strong preference for cheap activities
        if activity.price == 0:
            score += 15

        elif activity.price < 20:
            score += 5
        
        # Heavy penalty for expensive activities
        else:
            score -= activity.price * 0.8 
    
    # Otherwise if cost is not listed as a priority
    else:
        # Small bonus for free activities
        if activity.price == 0:
            score += 5  
        
        # Light penalty based on cost
        else:
            score -= activity.price * 0.15 
    
    # 3. SCHEDULE TYPE FIT (0-15 points)
    if prefs.schedule_type == "relaxed":
        if activity.duration <= 2:
            score += 15
        elif activity.duration >= 4:
            score -= 10  # Penalize long activities
    elif prefs.schedule_type == "packed":
        if activity.duration >= 2:
            score += 10
    
    # Otherwise if schedule type is balanced
    else:  
        if 1.5 <= activity.duration <= 3:
            score += 10
    
    # 4. VARIETY BONUS/PENALTY (-20 to +10 points)
    # Encourage diverse itinerary and penalize repetition
    category_counts = {}

    # Check what has already been scheduled
    for scheduled in already_scheduled:
        cat = (scheduled.category or "").lower()
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    current_cat = activity.category.lower()
    count = category_counts.get(current_cat, 0)
    
    # Give a bonus for an activity of a new category
    if count == 0:
        score += 10 
    
    # No penalty for a second activity of the same type
    elif count == 1:
        score += 0  # Neutral
    
    # Penalize if the activity would be the third of the same type
    elif count == 2:
        score -= 10  
    
    # Give a strong penalty for 4+ activities of the same type
    else:
        score -= 20 
    
    # 5. DURATION FLEXIBILITY (0-8 points)
    # Boost shorter activities as they are more flexible for scheduling
    if activity.duration <= 1:
        score += 8
    elif activity.duration <= 2:
        score += 5
    elif activity.duration <= 3:
        score += 2
    # No bonus or penalty for activities over 3 hours
    
    # Return the calculated score
    return score


def score_all_activities(activities, prefs, already_scheduled = None):
    '''
    Score ALL activities and return sorted list based on their score.

    **Parameters**

        activity: *Activity*
            Activity to score

        prefs: *UserPreferences*
            User preferences

        already_scheduled: *list[Activity]*
            Activities already in itinerary (for variety)
            Defaults to None.
 
    Returns:

        scored: *list[tuple[float, Activity]]*
            List of (score, activity) tuples sorted by score (highest score first)
    '''
    # Initialize empty list for storage
    scored = []

    # For all activities,
    for activity in activities:

        # Calculate a score for the activity
        score = score_activity(activity, prefs, already_scheduled)
        
        # Append a tuple of the activity and its score to the list of scored activities
        scored.append((score, activity))
    
    # Sort scored activities in descending order (highest to lowest)
    scored.sort(reverse=True, key=lambda x: x[0])
    
    # Return sorted list of scored activities
    return scored


def analyze_category_distribution(activities):
    '''
    Analyze the distribution of activity categories.
    Useful for understanding what's available.
    
    **Parameters**

        activities: *list[Activity]*
            List of Activity class objects containing the activities available.

    **Returns**

        distribution: *dict[str, int]*
            Dictionary mapping category -> count
    '''
    # Initialize empty variable for storage
    distribution = {}

    # For each activity,
    for activity in activities:

        # Get the category it belows to
        cat = activity.category.lower()

        # Increment the counter for the category the activity belongs to
        distribution[cat] = distribution.get(cat, 0) + 1

    # Return the calculated distribution of activities by category
    return distribution


def suggest_interest_balance(available_activities, user_interests):
    '''
    Suggest if user should adjust interests based on what's available.
    
    **Parameters**

    available_activities: *list[Activity]*
        List of available activities in the destination

    user_interests: *list[str]*
        List of user indicated interests.

    Returns:
        suggestions: *dict[str, str]*
            Dictionary with suggestions
    '''
    distribution = analyze_category_distribution(available_activities)
    suggestions = {}
    
    # For each indicated interests
    for interest in user_interests:

        # Count the number of activities available for that interest + suggest accordingly
        count = distribution.get(interest.lower(), 0)
        if count == 0:
            suggestions[interest] = f"No {interest} activities available in this destination"
        elif count < 3:
            suggestions[interest] = f"Limited {interest} options ({count} activities)"
    
    # Suggest unexplored categories
    for category, count in distribution.items():
        if category not in [i.lower() for i in user_interests] and count >= 5:
            suggestions[f"Consider {category}"] = f"{count} {category} activities available"
    
    # Return suggestion for each interest
    return suggestions
