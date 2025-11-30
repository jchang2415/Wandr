# Preferences Class

from dataclasses import dataclass
from typing import List

@dataclass
class UserPreferences:
    '''
    "User preferences" class object to hold user indicated preferences.
    Preferences include:
    - Interested activity categories (e.g. ["museum", "nature", "food"])
    - Trip budget
    - Trip type (e.g. relaxed, balanced, packed)
    - Prioritized aspect (e.g.cost, distance)
    '''
    # Define attributes
    interests: List[str]             
    budget: float                      
    schedule_type: str                  

    # Additional tuning knobs
    min_hours_per_day: float = 3.0
    max_hours_per_day: float = 8.0

    prioritize_cost: bool = False
    prioritize_distance: bool = False
    include_opening_hours: bool = False