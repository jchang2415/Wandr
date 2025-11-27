# Day Plan Class Code
'''
Code for defining the "DayPlan" class that will hold all the information for the itinerary of a day.
'''

from dataclasses import dataclass, field
from datetime import date
from typing import List
from .activity import Activity

@dataclass
class DayPlan:
    """
    Represents the plan for a single day in the itinerary.
    It contains:
    - the date of the day
    - a list of activities scheduled for that day
    """

    # Define "date" attribute
    date: date

    # Define "activities" attribute as a list of Activity class objects
    activities: List[Activity] = field(default_factory=list)

    # Define a method for calculating total cost of all activities in a day
    def total_cost(self) -> float:
        """
        Sum the total cost of all activities for that day.
        """
        return sum(a.price for a in self.activities)

    # Define a method for calculating total time for all activities in a day
    def total_duration(self) -> float:
        """
        Sum the total time for all activities for that day.
        """
        return sum(a.duration_hours for a in self.activities)

    # Define a method for adding a new Activity object to a Day Plan object
    def add_activity(self, activity: Activity) -> None:
        """
        Add an activity to the day's schedule.
        """
        self.activities.append(activity)

    # Define a method for converting a DayPlan class object to a dictionary
    def to_dict(self):
        """
        Convert this DayPlan into a dictionary for saving to JSON files.
        """
        return {
            "date": self.date.isoformat(),
            "activities": [a.to_dict() for a in self.activities]
        }