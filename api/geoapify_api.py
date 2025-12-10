# Code for Integrating Geoapify Points of Interest API #
'''
Geoapify API Integration
Fetches tourist attractions and places for any destination

API Documentation: https://www.geoapify.com/places-api
Free tier: 3,000 requests/day, no credit card required
'''

import requests
import os
from dotenv import load_dotenv
from models.activity import Activity

# Load environment variables
load_dotenv()

# Define a class for easier and simpler API interaction
class GeoapifyAPI:
    '''
    Client for Geoapify Places API.
    
    Get API key from: https://www.geoapify.com/
    '''
    
    def __init__(self, api_key = None):
        '''
        Initialize the API client when object is initialized.
        
        **Parameters**

            api_key: *str*
                Geoapify API key (or loads from .env)

        **Return**
            
            None
        '''
        # Set api_key attribute using argument or environment
        self.api_key = api_key or os.getenv('GEOAPIFY_API_KEY')
        if not self.api_key:
            raise ValueError("Geoapify API key not found. Set GEOAPIFY_API_KEY in .env file")
        
        # Set base_url attribute
        self.base_url = "https://api.geoapify.com/v2"
    
    def geocode_city(self, city_name):
        '''
        Method to get coordinates and details for a city.
        
        **Parameters**

            city_name: *str*
                Name of the city (e.g., "Paris", "Tokyo")
        
        **Returns**

            Dictionary with city details including coordinates or None
        '''
        # Set URL
        url = f"{self.base_url}/geocode/search"
        
        # Set search parameters using inputs
        params = {
            'text': city_name,
            'type': 'city',
            'format': 'json',
            'apiKey': self.api_key
        }
        
        # Retrieve the information from the API
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # If successful, retrieve and reformat information retrieved
            if data.get('results'):
                result = data['results'][0]
                return {
                    'name': result.get('formatted'),
                    'lat': result.get('lat'),
                    'lon': result.get('lon'),
                    'country': result.get('country'),
                    'city': result.get('city'),
                    'bbox': result.get('bbox')  # Bounding box
                }
            
            # Otherwise indicate that the city could not be found in the API database
            else:
                print(f"Could not find city '{city_name}'")
                return None
                
        except requests.RequestException as e:
            print(f"Error geocoding city: {e}")
            return None
    
    def get_places_in_city(self, city_name, categories, limit = 50, radius = 5000):
        '''
        Method to get places/attractions in a city.
        
        **Parameters*

            city_name: *str*
                Name of the city

            categories: *list[str]*
                Filter by categories (see category list below)
                    
                    Available categories (main ones):
                        - tourism.attraction
                        - tourism.sights
                        - entertainment.museum
                        - entertainment.culture
                        - leisure.park
                        - catering.restaurant
                        - commercial.shopping_mall
                        - activity
                    Full list: https://apidocs.geoapify.com/docs/places/#categories

            limit: *int*
                Maximum number of results
                Default value is 50.

            radius: *int*
                Search radius in meters from city center
                Default value is 5000
        
        **Returns**
            List of place dictionaries
        '''
        # First, get city coordinates
        city_info = self.geocode_city(city_name)
        if not city_info:
            return []
        
        lat, lon = city_info['lat'], city_info['lon']
        
        # Build search URL
        url = f"{self.base_url}/places"
        
        # Set default categories if none are provided
        if not categories:
            categories = [
                'tourism.attraction',
                'tourism.sights',
                'entertainment.museum',
                'entertainment.culture',
                'leisure.park'
            ]
        
        # Set up search parameters
        params = {
            'categories': ','.join(categories),
            'filter': f'circle:{lon},{lat},{radius}',
            'limit': limit,
            'apiKey': self.api_key
        }
        
        # Retrieve information from API
        try:
            print(f"🔍 Searching for places in {city_name}...")
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            places = data.get('features', [])
            print(f"Found {len(places)} places")
            return places
            
        except requests.RequestException as e:
            print(f"Error fetching places: {e}")
            return []
    
    def get_place_details(self, place_id):
        '''
        Method for getting detailed information about a specific place.
        
        **Parameters**

            place_id: *str*
                Unique identifier for the place
        
        **Returns**

            Detailed place dictionary or None
        '''
        # Set URL
        url = f"{self.base_url}/place-details"

        # Set up parameters for search
        params = {
            'id': place_id,
            'apiKey': self.api_key
        }
        
        # Get the information from the API
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('features', [None])[0]
        except requests.RequestException as e:
            print(f"Could not fetch details for {place_id}: {e}")
            return None
    
    def places_to_activities(self, places):
        '''
        Function for converting Geoapify places to Activity objects so we can integrate it into my program.
        
        **Parameters**
            
            places: *list[dict]*
                List of place dicts from get_places_in_city()
        
        **Returns**
           
           activities: *list[Activity]*
                List of Activity objects with all the Geoapify places inputted.
        '''
        # Initialize empty list to store our activity objects
        activities = []
        
        # Iterate through list of places
        for place in places:
            try:

                # Parse out information from the dictionary for each place
                properties = place.get('properties', {})
                geometry = place.get('geometry', {})
                
                name = properties.get('name') or properties.get('address_line1', 'Unknown')
                if not name or name == 'Unknown':
                    continue
                
                # Get location
                coordinates = geometry.get('coordinates', [])
                if len(coordinates) >= 2:
                    lon, lat = coordinates[0], coordinates[1]
                    location = (lat, lon)
                else:
                    location = None
                
                # Determine category from Geoapify categories
                categories = properties.get('categories', [])
                category = self._map_categories_to_type(categories)
                
                # Get description (if available)
                description = properties.get('description', '')
                if not description:
                    # Build description from available data
                    address = properties.get('address_line2', '')
                    if address:
                        description = f"Located at {address}"
                
                # Estimate duration and price
                duration_hours = self._estimate_duration(categories, category)
                price = self._estimate_price(categories, category, properties)
                
                # Create Activity object using parsed information
                activity = Activity(
                    name=name,
                    category=category,
                    duration_hours=duration_hours,
                    price=price,
                    location=location,
                    description=description
                )
                
                # Add the Activity object to our list of objects
                activities.append(activity)
                
            # Error handling
            except Exception as e:
                print(f"Skipping place: {e}")
                continue
        
        # Print statement for tracking progress
        print(f"Converted {len(activities)} places to activities")
        
        # Return list of Activity objects
        return activities
    
    def _map_categories_to_type(self, categories):
        '''
        Map Geoapify categories to my own activity types used in the program.

        **Parameters**

            categories: *list[str]*
                List of Geoapify category(ies) listed for an object

        **Returns**

            *str*
                String with the category the Activity belongs to
        '''
        categories_str = ','.join(categories).lower()
        
        # Search through categories one by one to match to our categories
        if any(cat in categories_str for cat in ['museum', 'gallery', 'art']):
            return 'museum'
        elif any(cat in categories_str for cat in ['park', 'garden', 'nature', 'outdoor']):
            return 'nature'
        elif any(cat in categories_str for cat in ['restaurant', 'food', 'cafe', 'catering']):
            return 'food'
        elif any(cat in categories_str for cat in ['shop', 'mall', 'commercial']):
            return 'shopping'
        elif any(cat in categories_str for cat in ['entertainment', 'theatre', 'cinema']):
            return 'entertainment'
        elif any(cat in categories_str for cat in ['tourism', 'attraction', 'sights', 'monument']):
            return 'landmark'
        elif 'activity' in categories_str:
            return 'tour'
        else:
            return 'landmark'
    
    def _estimate_duration(self, categories, category):
        '''
        Function for estimating duration in hours based on category in case information is unavailable.

        **Parameters**

            categories: *list[str]*
                List of categories that an Activity is listed under in Geoapify

            category: *str*
                Category (in Wandr) that an activity is listed under

        **Returns**

            *float*
                Duration (in hours) that an activity is estimated to take.
        '''
        categories_str = ','.join(categories).lower()
        
        # Go through categories and make an estimate based on the category it belongs to
        if 'museum' in categories_str or category == 'museum':
            return 2.5
        elif category == 'nature' or 'park' in categories_str:
            return 1.5
        elif category == 'food':
            return 1.5
        elif category == 'shopping':
            return 2.0
        elif category == 'entertainment':
            return 2.5
        
        # Otherwise, default to assigning the activity a 1 hour duration
        else:
            return 1.0
    
    def _estimate_price(self, categories, category, properties):
        '''
        Function for estimating price (in USD) based on category type in case information is not available.
        
        **Parameters**

            categories: *list[str]*
                List of categories that an Activity is listed under in Geoapify

            category: *str*
                Category (in Wandr) that an activity is listed under

            properties: *dict*
                Properties of activity as indicated by API.

        **Returns**

            *float*
                Estimated price (in USD) of the activity.

        '''
        categories_str = ','.join(categories).lower()
        
        # Check if it's free (parks, monuments)
        if any(cat in categories_str for cat in ['park', 'garden', 'square', 'street']):
            return 0.0
        
        # Price estimate for museums and attractions
        if category == 'museum' or 'museum' in categories_str:
            return 15.0
        
        # Price estimate for food
        if category == 'food':
            return 25.0
        
        # Price estimate for entertainment
        if category == 'entertainment':
            return 40.0
        
        # Price estimate for shopping
        if category == 'shopping':
            return 0.0
        
        # Check if it has opening hours (usually means paid entry)
        if properties.get('opening_hours'):
            return 10.0
        
        # Otherwise default to a value of 5 USD
        return 5.0


# Convenience function
def fetch_activities_for_city(city_name, categories = None, limit = 50, radius = 5000):
    '''
    Simple compiled function to fetch activities for a city using Geoapify.
    Combines all previous code into more usable single function.
    
    **Parameters**

        city_name: *str*
            Name of city
            (e.g., "Paris", "Tokyo")

        categories: *list[str]*
            Optional list of Geoapify categories to filter by

        limit: *int* 
            Max number of activities.
            Default value is 50.

        radius: *int*
            Search radius in meters.
            Default value is 5000.
    
    **Returns**
        activities: *list[Activity]*
            List of Activity objects obtained for the city in question
    
    Example:
        activities = fetch_activities_for_city("Paris", limit=30)
    '''
    # Initialize API object to call API
    api = GeoapifyAPI()

    # Obtain points of interest for the city
    places = api.get_places_in_city(city_name, categories, limit, radius)

    # Convert API JSON information to Activity class objects for program use
    activities = api.places_to_activities(places)

    # Return obtained list of Activity class object containing points of interest for the city
    return activities


def get_comprehensive_activities(city_name, total_limit):
    '''
    Get a comprehensive list of activities across all categories.
    Makes multiple API calls to get diverse results.
    
    **Parameters**

        city_name: *str* 
            Name of city

        total_limit: *int*
            Total activities to aim for.
            Default value is 60.
    
    **Returns**

        unique_activities: *list[Activity]*
            List of Activity objects across all categories
    '''
    # Initialize API client
    api = GeoapifyAPI()

    # Initialize empty list to hold all activities we find
    all_activities = []
    
    # Define category groups that Geoapify categories can be lumped into
    category_groups = {
        'attractions': ['tourism.attraction', 'tourism.sights'],
        'museums': ['entertainment.museum', 'entertainment.culture'],
        'parks': ['leisure.park', 'natural'],
        'food': ['catering.restaurant', 'catering.cafe'],
        'shopping': ['commercial.shopping_mall', 'commercial.marketplace'],
        'entertainment': ['entertainment', 'sport']
    }
    
    # Ensure that an even number of points from each category is shown
    per_category = total_limit // len(category_groups)
    
    # Loop through each bucket of POI types
    for group_name, categories in category_groups.items():
        print(f"📍 Fetching {group_name}...")

        # Retrieve calculated number of POIs from the category from API
        places = api.get_places_in_city(city_name, categories, per_category, radius=7000)
        
        # Convert POIs to Activity class objects
        activities = api.places_to_activities(places)

        # Add all items retrieved to our list of POIs
        all_activities.extend(activities)
    
    # Remove duplicates by name
    seen_names = set()
    unique_activities = []
    for activity in all_activities:
        if activity.name not in seen_names:
            seen_names.add(activity.name)
            unique_activities.append(activity)
    
    print(f"Total unique activities: {len(unique_activities)}")
    
    # Return retrieved unique activities
    return unique_activities


# Example usage for testing API
if __name__ == "__main__":
    print("Testing Geoapify API...\n")
    
    # Test 1: Basic activity fetch
    print("Test 1: Fetching activities for Paris\n")
    activities = fetch_activities_for_city("Paris", limit=10)
    
    print(f"\nFound {len(activities)} activities:")
    for i, act in enumerate(activities[:5], 1):
        print(f"\n{i}. {act.name}")
        print(f"   Category: {act.category}")
        print(f"   Duration: {act.duration_hours}h")
        print(f"   Price: ${act.price}")
        if act.location:
            print(f"   Location: {act.location}")
    
    # Test 2: Comprehensive fetch
    print("\n" + "="*60)
    print("Test 2: Comprehensive activity fetch\n")
    all_activities = get_comprehensive_activities("Paris", total_limit=30)
    
    # Show category distribution
    from collections import Counter
    categories = Counter(act.category for act in all_activities)
    print("\nCategory distribution:")
    for cat, count in categories.items():
        print(f"  {cat}: {count}")
