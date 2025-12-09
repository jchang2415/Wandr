# Activity.py

'''
Define
'''

from dataclasses import dataclass

@dataclass
class Activity:
    '''
    This defines a class called "Activity" to store our things to do in our app. 
    These activities have an associated name, category, duration (in hours), cost (in USD), location, and description.
    These activities can be assembled to form itineraries.
    '''
    # Define "name" attribute
    name: str

    # Define "category" attribute
    category: str
    
    # Define "duration" attribute; in HOURS
    duration: float

    # Define "cost" attribute; in USD
    cost: float

    # Define "location" attribute; in (latitude, longitude) aka GPS coordinates
    location: tuple[float, float]

    # Define "description" attribute to describe the activity
    description: str

    # Define method for converting Activity class objects to dictionaries
    def to_dict(self):
        '''
        Converts the an object of the Activity class to a standard Python dictionary so we can
        save it into JSON files later.
        '''

        return {
            "name": self.name,
            "category": self.category,
            "duration_hours": self.duration,
            "price": self.price,
            "location": self.location,
            "description": self.description,
        }



