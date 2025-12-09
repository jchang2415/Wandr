# Trip Class Code

from dataclasses import dataclass, field
from datetime import date
from typing import List
from .dayplan import DayPlan

@dataclass
class Trip:
    """
    Represents the entire trip a user is planning.
    Includes:
    - destination
    - start and end dates
    - interests
    - budget
    - itinerary (list of DayPlans)
    """
    # Define attributes
    destination: str
    start_date: date
    end_date: date
    budget: float
    interests: List[str]
    itinerary: List[DayPlan] = field(default_factory=list)

    # Define method for returning total length of trip in days
    def trip_length(self) -> int:
        """
        Return the number of days in the trip.
        """
        return (self.end_date - self.start_date).days + 1

    # Define method for converting Trip class objects to a dictionary
    def to_dict(self):
        """
        Convert to a JSON-serializable dictionary.
        """
        return {
            "destination": self.destination,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "budget": self.budget,
            "interests": self.interests,
            "itinerary": [d.to_dict() for d in self.itinerary]

        }
