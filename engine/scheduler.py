# Itinerary Builder with Geographic Clustering + Distance Calculations

from datetime import timedelta
from models.activity import Activity
from models.trip import Trip
from models.preferences import UserPreferences
from models.dayplan import DayPlan
from engine.scorer import score_activity
from utils.haversine import haversine_distance_km

def create_itinerary(trip, activities, prefs, locked_activities = None):
    """
    Enhanced scheduler that:
    - Scores activities based on preferences
    - Groups activities by geographic proximity
    - Respects locked activities
    - Optimizes daily routes to minimize travel

    **Parameters**

        trip: *Trip*
            Trip class object that we want to make an itinerary for

        activities: *list[Activity]*
            List of Activity class objects containing all activities available.

        prefs: *UserPreferences*
            UserPreferences class object that contains the user-indicated preferences

        locked_activities: *list[Activity]*
            List of Activity class object containing the activities that the User has indicated they want to lock into the final itinerary
            Defaults to None.

    **Returns**

        itinerary: *list[DayPlan]*
            List of DayPlan objects (one for each day) that contains the final itinerary generated for the trip.

    """
    # Initialize list of locked_activities based on passed argument; otherwise initialize as empty list
    locked_activities = locked_activities or []
    
    # Score all available activities using scorer
    scored_activities = [(score_activity(a, prefs), a) for a in activities]

    # Sort activities based on score from best to worst
    scored_activities.sort(reverse=True, key=lambda x: x[0])
    
    # Initialize variables for looping
    itinerary = []
    current_date = trip.start_date
    remaining_budget = trip.budget
    used = set()
    
    # Mark locked activities as used and ensure they're scheduled
    locked_by_day = {}  # Track if user wants locked activities on specific days
    
    while current_date <= trip.end_date:
        day = DayPlan(date=current_date)
        hours_left = prefs.max_hours_per_day
        
        # First add any locked activities for the day
        for locked_act in locked_activities:
            if locked_act not in used:
                if locked_act.duration_hours <= hours_left:
                    day.add_activity(locked_act)
                    used.add(locked_act)
                    hours_left -= locked_act.duration_hours
                    remaining_budget -= locked_act.price
                    break 
        
        # Fill the rest of the day with geographically clustered activities
        if day.activities:

            # Start clustering around the locked activity
            last_location = day.activities[-1].location
        
        # Otherwise start with the highest scoring activity that fits the schedule
        else:

            last_location = None
            for score, activity in scored_activities:
                if activity not in used and activity.duration_hours <= hours_left:
                    if remaining_budget - activity.price >= 0:
                        day.add_activity(activity)
                        used.add(activity)
                        hours_left -= activity.duration_hours
                        remaining_budget -= activity.price
                        last_location = activity.location
                        break
        
        # Fill remaining time with nearby activities
        while hours_left > 0:
            best_nearby = None
            best_score = -float('inf')
            
            for score, activity in scored_activities:
                if activity in used:
                    continue
                
                # Check constraints
                if activity.duration_hours > hours_left:
                    continue
                if remaining_budget - activity.price < 0:
                    continue
                
                # Calculate proximity bonus if we have a location
                proximity_bonus = 0
                if last_location and activity.location:
                    distance = haversine_distance_km(last_location, activity.location)
                    # Bonus for activities within 2km, penalty for far ones
                    if distance < 2:
                        proximity_bonus = 20 - (distance * 5)  # Up to +20 points
                    elif distance > 5:
                        proximity_bonus = -10  # Penalty for far activities
                
                adjusted_score = score + proximity_bonus
                
                if adjusted_score > best_score:
                    best_score = adjusted_score
                    best_nearby = activity
            
            # Add the best nearby activity
            if best_nearby:
                day.add_activity(best_nearby)
                used.add(best_nearby)
                hours_left -= best_nearby.duration_hours
                remaining_budget -= best_nearby.price
                last_location = best_nearby.location
            else:
                break  # No more suitable activities
        
        # Add the finalized DayPlan object with the schedule for a single day to itinerary
        itinerary.append(day)

        # Increment the day counter
        current_date += timedelta(days=1)
    
    # Return generated activity
    return itinerary


def get_activity_clusters(activities, max_distance_km = 2.0):
    '''
    Group activities into geographic clusters based on proximity.
    Useful for suggesting which activities work well together.
    
    **Parameters**

        activities: *list[Activity]*
            List of activities to cluster

        max_distance_km: *float*
            Maximum distance to consider activities in same cluster
            Defaults to 2.0
    
    Returns:

        clusters: *list[list[Activity]]*
            List of activity clusters generated (each cluster itself is a list of activities)
    '''
    # Initialize variables
    clusters = []
    used = set()
    
    # For each activity
    for activity in activities:
        if activity in used or not activity.location:
            continue
        
        # Start new cluster
        cluster = [activity]
        used.add(activity)
        
        # Find nearby activities
        for other in activities:
            if other in used or not other.location:
                continue
            
            distance = haversine_distance_km(activity.location, other.location)
            if distance <= max_distance_km:
                cluster.append(other)
                used.add(other)
        
        if len(cluster) > 1:  # Only keep clusters with multiple activities
            clusters.append(cluster)
    
    return clusters


def estimate_travel_time(activity1, activity2, speed_kmh = 5.0):
    '''
    Estimate travel time between two activities in hours.
    Assumes walking at average speed.
    
    **Parameters**

        activity1: *Activity*
            Starting activity

        activity2: *Activity*
            Destination activity  

        speed_kmh: *float*
            Average travel speed in km/h (defaults to 5 km/h for walking)
    
    **Returns**
        
        travel_time: *float*
            Estimated travel time in hours
    '''
    if not activity1.location or not activity2.location:
        return 0.25  # Default 15 minutes if no location data
    
    # Calculate distance between two activities using Haversine distance
    distance = haversine_distance_km(activity1.location, activity2.location)

    # Use distance to calculate travel time between two activities
    travel_time = distance / speed_kmh
    
    # Add 15 min buffer for navigation/waiting & return travel_time value
    return travel_time + 0.25  


