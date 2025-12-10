# Amadeus Flight API Integration
"""
Code for integrating API from Amadeus for real-time flight price searching.
"""

import os
from datetime import date, timedelta
from dotenv import load_dotenv
from amadeus import Client, ResponseError

# Load environment variables (e.g. API keys)
load_dotenv()

# Define class for communicating with the API for simplicity
class AmadeusFlightAPI:
    """
    Client for Amadeus Flight API.
    
    Documentation: https://developers.amadeus.com/self-service/category/flights
    """
    
    def __init__(self, api_key, api_secret):
        """
        Initialize Amadeus client.
        
        **Parameters**

            api_key: *str*
                Amadeus API key (or loads from .env)

            api_secret: *str*
                Amadeus API secret (or loads from .env)
        """
        # Get API keys from argument or environment
        api_key = api_key or os.getenv('AMADEUS_API_KEY')
        api_secret = api_secret or os.getenv('AMADEUS_API_SECRET')
        
        # Indicate if API keys not found
        if not api_key or not api_secret:
            raise ValueError("Amadeus credentials not found. Set AMADEUS_API_KEY and AMADEUS_API_SECRET in .env")
        
        # Create connection to API using keys under "client" attribute
        self.client = Client(
            client_id=api_key,
            client_secret=api_secret
        )
    
    def _parse_flight_offer(self, flight_offer):
        '''
        Parse Amadeus flight offer into simpler format.
        
        **Parameters*

            flight_offer: *dict*
                A flight offer in JSON (Dictionary) format, returned from the API call.

        **Returns**
            parsed: *dict*
                Dictionary with key flight information in a more manageable form
        '''
        # Obtain price and itinerary information
        price = flight_offer.get('price', {})
        itineraries = flight_offer.get('itineraries', [])
        
        # Get first itinerary details (outbound)
        outbound = itineraries[0] if itineraries else {}
        segments = outbound.get('segments', [])
        
        # Calculate total duration
        duration = outbound.get('duration', 'Unknown')
        
        # Get airline info
        first_segment = segments[0] if segments else {}
        carrier_code = first_segment.get('carrierCode', 'Unknown')
        
        # Count number of stops
        stops = len(segments) - 1
        
        # Parse departure and arrival times
        departure = first_segment.get('departure', {})
        arrival = segments[-1].get('arrival', {}) if segments else {}
        
        # Organize parsed information into a dictionary
        parsed = {
            'total_price': float(price.get('total', 0)),
            'currency': price.get('currency', 'USD'),
            'departure_date': departure.get('at', '').split('T')[0],
            'arrival_date': arrival.get('at', '').split('T')[0],
            'departure_time': departure.get('at', '').split('T')[1] if 'T' in departure.get('at', '') else '',
            'arrival_time': arrival.get('at', '').split('T')[1] if 'T' in arrival.get('at', '') else '',
            'duration': duration,
            'stops': stops,
            'airline': carrier_code,
            'origin': departure.get('iataCode', ''),
            'destination': arrival.get('iataCode', ''),
        }
        
        # Add return flight info if necessary
        if len(itineraries) > 1:
            return_itinerary = itineraries[1]
            return_segments = return_itinerary.get('segments', [])
            if return_segments:
                parsed['return_departure'] = return_segments[0].get('departure', {}).get('at', '')
                parsed['return_arrival'] = return_segments[-1].get('arrival', {}).get('at', '')
        
        # Return parsed and formatted flight information
        return parsed

    def search_flights(self, origin, destination, departure_date, return_date = None, adults = 1, max_results = 10, currency = "USD"):
        '''
        Method for searching for flights between two cities.
        
        **Parameters**

            origin: *str* 
                Letter code for airport of origin (e.g., "JFK", "LAX")

            destination: *str*
                Letter code for airport of destination 
                (e.g., "CDG" for Paris)

            departure_date: *date*
                Date of departure

            return_date: *date*
                Date of return (None for one-way)

            adults: *int*
                Number of adult passengers
                Default value is 1.

            max_results: *int*
                Maximum number of results to return from the API.
                Default value is 10.

            currency: *str*
                Currency for prices
                Default value is "USD"
        
        **Returns**

            flights: *List[Dict]*
                List of flight offers, each of which is a dictionaries
        
        Example:
            flights = api.search_flights("JFK", "CDG", date(2025, 6, 15), date(2025, 6, 22))
        '''
        try:
            print(f"Searching flights {origin} → {destination}...")
            
            # Build search parameters from method input
            search_params = {
                'originLocationCode': origin.upper(),
                'destinationLocationCode': destination.upper(),
                'departureDate': departure_date.isoformat(),
                'adults': adults,
                'max': max_results,
                'currencyCode': currency
            }
            
            # Add return date if provided
            if return_date:
                search_params['returnDate'] = return_date.isoformat()
            
            # Execute search using the API client
            response = self.client.shopping.flight_offers_search.get(**search_params)
            
            flights = response.data
            print(f"Found {len(flights)} flight options")
            
            # Return retrieved information from the API
            return flights
            
        except ResponseError as error:
            print(f"Amadeus API Error: {error}")
            return []
    
    def get_cheapest_flights(self, origin, destination, departure_date, return_date = None, adults = 1):
        '''
        Method for getting the single CHEAPEST flight option.
        
        **Parameters**
        
        origin: *str* 
                Letter code for airport of origin (e.g., "JFK", "LAX")

            destination: *str*
                Letter code for airport of destination 
                (e.g., "CDG" for Paris)

            departure_date: *date*
                Date of departure

            return_date: *date*
                Date of return (None for one-way)

            adults: *int*
                Number of adult passengers
                Default value is 1.


        **Returns**

            Dictionary with cheapest flight details or None
        '''
        # Use search_flights method to get available flights
        flights = self.search_flights(origin, destination, departure_date, return_date, adults, max_results=20)
        
        # If no flights are found, indicate as such
        if not flights:
            return None
        
        # Find cheapest by total price
        cheapest = min(flights, key=lambda f: float(f['price']['total']))

        # Parse the info from the cheapest flight found and return it
        return self._parse_flight_offer(cheapest)
    
    def search_flexible_dates(self, origin, destination, target_date, date_range_days = 3, return_after_days = 7):
        '''
        Search for flights across a range of dates to find best prices.
        
        **Parameters**
        
            origin: *str* 
                Letter code for airport of origin (e.g., "JFK", "LAX")

            destination: *str*
                Letter code for airport of destination 
                (e.g., "CDG" for Paris)

            target_date: *date*
                Ideal date of departure

            date_range_days: *int*
                How many days +/- to check around the target date
                Default value is 3.

            return_after_days: *int*
                Number of days after departure to return.
                Default value is 7.
        
        **Returns**
            
            List of top 10 cheapeast parsed flight options sorted by price
        '''
        # Initialize empty list to hold all options we find
        all_options = []
        
        # Search across date range using API call
        for offset in range(-date_range_days, date_range_days + 1):
            dep_date = target_date + timedelta(days=offset)
            ret_date = dep_date + timedelta(days=return_after_days)
            
            flights = self.search_flights(origin, destination, dep_date, ret_date, max_results=5)
            
            for flight in flights:
                parsed = self._parse_flight_offer(flight)
                parsed['flexibility_offset'] = offset  # Track how far from target date each flight is
                all_options.append(parsed)
        
        # Sort flights found by price
        all_options.sort(key=lambda x: x['total_price'])
        
        # Return the 10 cheapest flights
        return all_options[:10]
    
    def get_airport_code(self, city_name):
        """
        Search for airport code by city name. Backup hard-coded three-letter airport codes if broader data is not available.
        
        **Parameters**

            city_name: *str*
                City name (e.g., "Paris", "New York")
        
        **Returns**
            
            Three letter primary airport code (IATA) or None
        """
        # Hard code starter dictionary with common city to airport mappings
        city_to_airport = {
            'paris': 'CDG',
            'london': 'LHR',
            'new york': 'JFK',
            'nyc': 'JFK',
            'tokyo': 'NRT',
            'los angeles': 'LAX',
            'chicago': 'ORD',
            'san francisco': 'SFO',
            'miami': 'MIA',
            'seattle': 'SEA',
            'boston': 'BOS',
            'washington': 'IAD',
            'madrid': 'MAD',
            'barcelona': 'BCN',
            'rome': 'FCO',
            'amsterdam': 'AMS',
            'berlin': 'BER',
            'dubai': 'DXB',
            'singapore': 'SIN',
            'hong kong': 'HKG',
            'sydney': 'SYD',
            'toronto': 'YYZ',
            'vancouver': 'YVR',
        }
        
        # Process formatting of inputted city name
        city_lower = city_name.lower().strip()

        # Return the code determined for the city
        return city_to_airport.get(city_lower)
    
    def display_flight_options(self, flights):
        '''
        Helper method to display flight options in a more readable format.

        **Parameters**

            flights: *list[dict]*
                List of dictionaries of flights as returned from the API.

        **Returns*

            None
        '''
        # Return nothing if flights is empty
        if not flights:
            print("No flights found.")
            return
        
        # Print out flight information in readable format in the command line
        print("\n" + "="*70)
        print("FLIGHT OPTIONS")
        print("="*70)
        
        for i, flight in enumerate(flights, 1):
            print(f"\n✈️  Option {i}: ${flight['total_price']:.2f} {flight['currency']}")
            print(f"   {flight['origin']} → {flight['destination']}")
            print(f"   Departure: {flight['departure_date']} {flight.get('departure_time', '')[:5]}")
            print(f"   Arrival: {flight['arrival_date']} {flight.get('arrival_time', '')[:5]}")
            print(f"   Duration: {flight['duration']}")
            print(f"   Stops: {flight['stops']}")
            print(f"   Airline: {flight['airline']}")
            
            if 'return_departure' in flight:
                print(f"   Return: {flight.get('return_departure', '').split('T')[0]}")


# Convenience function
def search_trip_flights(origin_city, destination_city, departure_date, return_date):
    """
    Final simple function to search for flights for a trip. Contains all the other functions wrapped into a simpler format.
    
    **Parameters**

        origin_city: *str*
            Origin city name 
            (e.g., "New York")

        destination_city: *str*
            Destination city name (e.g., "Paris")

        departure_date: *date*
            Departure date

        return_date: *date*
            Return date
    
    **Returns**
        cheapest: *dict*
            Cheapest flight details in dictionary format or None
    
    Example:
        flight = search_trip_flights("New York", "Paris", date(2025, 6, 15), date(2025, 6, 22))
    """
    try:
        # Initialize API
        api = AmadeusFlightAPI()
        
        # Get airport codes for the inputted cities
        origin = api.get_airport_code(origin_city)
        destination = api.get_airport_code(destination_city)
        
        # Catch errors if either of the origin or destination airport codes are not known
        if not origin:
            print(f"Unknown airport for '{origin_city}'")
            return None
        if not destination:
            print(f"Unknown airport for '{destination_city}'")
            return None
        
        # Search for cheapest flight
        cheapest = api.get_cheapest_flights(origin, destination, departure_date, return_date)
        
        # Return the cheapest flight found
        return cheapest
        
    except Exception as e:
        print(f"Error searching flights: {e}")
        return None


# Example usage for testing
if __name__ == "__main__":
    
    # Test the API
    print("Testing Amadeus Flight API...\n")
    
    # Search for a flight
    api = AmadeusFlightAPI()
    
    # Test example dates
    departure = date(2025, 5, 25)
    return_date = date(2025, 5, 30)
    
    # Try to search for flights
    flights = api.search_flights("JFK", "CDG", departure, return_date, max_results=5)
    
    if flights:
        parsed_flights = [api._parse_flight_offer(f) for f in flights]
        api.display_flight_options(parsed_flights)
    else:
        print("No flights found. Check your API credentials.")
