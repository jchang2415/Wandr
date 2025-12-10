# Main Code Block

"""
Main script for Wandr - Interactive Travel Planner
Integrates CSV loading, CLI interface, and scheduling engine.
"""

from datetime import date
from pathlib import Path

# Import your existing classes
from models.activity import Activity
from models.preferences import UserPreferences
from models.trip import Trip
from engine.scheduler import create_itinerary
from utils.csv_reader import load_activities_from_csv

# Import API (allows program to still run if API not working)
try:
    from api.geoapify_api import fetch_activities_for_city, get_comprehensive_activities
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False
    print("⚠️  API not available. Install: pip install requests python-dotenv")

try:
    from api.amadeus_api import AmadeusFlightAPI, search_trip_flights
    FLIGHT_API_AVAILABLE = True
except ImportError:
    FLIGHT_API_AVAILABLE = False
    print("⚠️  Amadeus Flight API not available.")

# Import GUI
try:
    from gui.gui import WandrGUI, main as gui_main
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    print("⚠️  GUI not available. Install: pip install tkinter")


def display_welcome():
    """Display welcome message and mode selection."""
    print("\n" + "="*60)
    print("WELCOME TO WANDR - YOUR INTERACTIVE TRAVEL PLANNER")
    print("="*60)
    print("\nChoose your interface:")
    print("1. GUI (Graphical Interface) - Recommended")
    print("2. CLI (Command Line Interface) - Advanced")
    print("3. Exit")


def get_user_inputs():
    '''
    Function for collecting all user inputs via the command line interface.

    **Parameters**

        None

    **Returns**

        *dict*
            Dictionary containing parsed user input.
    '''
    print("\n" + "="*60)
    print("WELCOME TO WANDR - YOUR INTERACTIVE TRAVEL PLANNER")
    print("="*60)
    
    # Prompt user for a destination
    destination = input("\nEnter your destination city: ").strip()
    
    # Prompt user for trip dates
    print("\n--- TRIP DATES ---")
    while True:
        date_str = input("Enter START date (YYYY-MM-DD): ").strip()
        try:
            start_date = date.fromisoformat(date_str)
            break
        
        # Ensure date entered is in valid format
        except ValueError:
            print("Invalid format. Please use YYYY-MM-DD (e.g., 2025-06-15)")
    
    while True:
        date_str = input("Enter END date (YYYY-MM-DD): ").strip()
        try:
            end_date = date.fromisoformat(date_str)
            if end_date >= start_date:
                break
            print("End date must be after start date.")
        
        # Ensure date entered is in valid format
        except ValueError:
            print("Invalid format. Please use YYYY-MM-DD")
    
    # Prompt user for desired total budget
    while True:
        try:
            budget = float(input("\nEnter your total budget (USD): $"))
            if budget > 0:
                break
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Prompt user for interests
    print("\n--- INTERESTS ---")
    print("Enter activity categories you're interested in (comma-separated)")
    print("Examples: museum, nature, food, tour, shopping")
    interests_str = input("Your interests: ").strip()
    interests = [i.strip() for i in interests_str.split(",")]
    
    # Prompt user for travel style
    print("\n--- TRAVEL STYLE ---")
    print("1. Relaxed (shorter activities, more breaks)")
    print("2. Balanced (mix of activities)")
    print("3. Packed (maximize activities)")
    
    schedule_map = {'1': 'relaxed', '2': 'balanced', '3': 'packed'}
    while True:
        choice = input("Choose travel style (1-3): ").strip()
        if choice in schedule_map:
            schedule_type = schedule_map[choice]
            break
        print("Please enter 1, 2, or 3.")
    
    # Prompt user for a cost priority
    prioritize_cost = input("\nPrioritize cheaper activities? (y/n): ").strip().lower() == 'y'

    # Check if user wants to check for flights as well
    search_flights = False
    origin_city = None
    if FLIGHT_API_AVAILABLE:
        search_flights = input("\nSearch for flights? (y/n): ").strip().lower() == 'y'
        if search_flights:
            origin_city = input("Enter your departure city: ").strip()
    
    # Return the gathered information in a formatted dictionary
    return {
        'destination': destination,
        'start_date': start_date,
        'end_date': end_date,
        'budget': budget,
        'interests': interests,
        'schedule_type': schedule_type,
        'prioritize_cost': prioritize_cost,
        'search_flights': search_flights,
        'origin_city': origin_city
    }

def display_itinerary(user_inputs, itinerary):
    '''
    Function for formatting final itinerary for displaying in CLI / writing to file
    '''
    print("\n" + "="*60)
    print("YOUR TRAVEL PLAN SUMMARY")
    print("="*60)
    
    # Display user input summary
    print("\n--- User Details ---")
    print(f"Destination: {user_inputs['destination']}")
    print(f"Start Date: {user_inputs['start_date']}")
    print(f"End Date: {user_inputs['end_date']}")
    print(f"Total Budget: ${user_inputs['budget']:.2f}")
    print(f"Interests: {', '.join(user_inputs['interests'])}")
    print(f"Travel Style: {user_inputs['schedule_type'].capitalize()}")
    print(f"Prioritize Cheaper Activities: {'Yes' if user_inputs['prioritize_cost'] else 'No'}")
    
    # Display itinerary
    print("\n--- Itinerary ---")
    total_cost = 0
    
    for i, day in enumerate(itinerary, 1):
        day_cost = sum(a.price for a in day.activities)
        total_cost += day_cost
        
        print(f"\nDAY {i} - {day.date}")
        print(f"   Total: {day.total_duration():.1f} hours, ${day_cost:.2f}")
        print("-" * 60)
        
        if not day.activities:
            print("   No activities scheduled")
        else:
            for j, activity in enumerate(day.activities, 1):
                print(f"   {j}. {activity.name}")
                print(f"      {activity.category} | "
                      f"{activity.duration_hours}h | "  # ← FIXED
                      f"${activity.price}")
                if activity.description:
                    desc = activity.description[:80] + "..." if len(activity.description) > 80 else activity.description
                    print(f"      {desc}")
    
    print("\n" + "="*60)
    print(f"TOTAL TRIP COST: ${total_cost:.2f} / ${trip.budget:.2f}")
    if total_cost <= trip.budget:
        remaining = trip.budget - total_cost
        print(f"✅ Within budget! (${remaining:.2f} remaining)")
    else:
        over = total_cost - trip.budget
        print(f"⚠️  Over budget by ${over:.2f}")
    print("="*60)


def search_flights_for_trip(origin_city, destination_city, start_date, end_date):
    """Search for flights and display results."""
    if not FLIGHT_API_AVAILABLE:
        print("\nFlight API not available")
        return None
    
    print("\n" + "="*60)
    print("FLIGHT SEARCH")
    print("="*60)
    
    try:
        flight = search_trip_flights(origin_city, destination_city, start_date, end_date)
        
        if flight:
            print(f"\n✈️  CHEAPEST FLIGHT FOUND")
            print(f"   Route: {flight['origin']} → {flight['destination']}")
            print(f"   Price: ${flight['total_price']:.2f} {flight['currency']}")
            print(f"   Departure: {flight['departure_date']} {flight.get('departure_time', '')[:5]}")
            print(f"   Arrival: {flight['arrival_date']} {flight.get('arrival_time', '')[:5]}")
            print(f"   Duration: {flight['duration']}")
            print(f"   Stops: {flight['stops']}")
            print(f"   Airline: {flight['airline']}")
            
            if 'return_departure' in flight:
                print(f"   Return: {flight.get('return_departure', '').split('T')[0]}")
            
            return flight
        else:
            print("\nNo flights found")
            return None
            
    except Exception as e:
        print(f"\nFlight search error: {e}")
        return None


def load_activities(destination, use_api = True):
    """
    Load activities for a destination.
    Try API first, fall back to CSV if needed.
    
    **Parameters**

        destination: *str*
            City name of destination

        use_api: *bool*
            Whether to try API first.
            Defaults to True
    
    **Returns**
        
        activities: *list[Activity]*
            List of Activity objects
    """
    activities = []
    
    # Try API first if available
    if use_api and API_AVAILABLE:
        try:
            print(f"\n Fetching activities from Geoapify API for {destination}...")
            activities = get_comprehensive_activities(destination, total_limit=50)
            
            if activities:
                print(f"Loaded {len(activities)} activities from API")
                return activities
            else:
                print("⚠️  API returned no results, trying CSV...")
        except Exception as e:
            print(f"⚠️  API failed: {e}")
            print("📂 Falling back to CSV data...")
    
    # Fall back to CSV
    csv_map = {
        'paris': 'paris',
        'tokyo': 'tokyo', 
        'new york': 'nyc',
        'new york city': 'nyc',
        'nyc': 'nyc',
    }
    
    dest_key = destination.lower().strip()
    file_base = csv_map.get(dest_key, dest_key.replace(' ', '_'))
    csv_path = Path(f"data/{file_base}_activities.csv")
    
    if not csv_path.exists():
        # Try sample data
        csv_path = Path("data/sample_data1.csv")
    
    if csv_path.exists():
        print(f"\n Loading activities from {csv_path}...")
        activities = load_activities_from_csv(csv_path)
        print(f"Loaded {len(activities)} activities from CSV")
        return activities
    
    # No data found
    raise FileNotFoundError(
        f"No data available for {destination}.\n"
        f"Please either:\n"
        f"  1. Set up Geoapify API (see README)\n"
        f"  2. Create data/{dest_key}_activities.csv"
    )

def run_cli_mode():
    '''
    Command line version entry point for the program.
    '''
    
    # Get user inputs
    user_inputs = get_user_inputs()
    
    # Search for flights if requested
    flight_info = None
    if user_inputs['search_flights'] and user_inputs['origin_city']:
        flight_info = search_flights_for_trip(
            user_inputs['origin_city'],
            user_inputs['destination'],
            user_inputs['start_date'],
            user_inputs['end_date']
        )
    
    # Ask about data source
    use_api = False
    if API_AVAILABLE:
        print("\n--- DATA SOURCE ---")
        use_api_input = input("Fetch activities from API? (y/n, default=y): ").strip().lower()
        use_api = use_api_input != 'n'
    
    # Load activities
    try:
        activities = load_activities(user_inputs['destination'], use_api=use_api)
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        return
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return
    
    if not activities:
        print("\n❌ No activities found.")
        return
    
    # Create Trip class object based on user input
    trip = Trip(
        destination=user_inputs['destination'],
        start_date=user_inputs['start_date'],
        end_date=user_inputs['end_date'],
        budget=user_inputs['budget'],
        interests=user_inputs['interests']
    )
    
    # Create UserPreferences class object based on user input
    preferences = UserPreferences(
        interests=user_inputs['interests'],
        budget=user_inputs['budget'],
        schedule_type=user_inputs['schedule_type'],
        prioritize_cost=user_inputs['prioritize_cost']
    )
    
    # Use engine to generate itinerary using info provided
    print("\n Building your personalized itinerary...")
    itinerary = create_itinerary(trip, activities, preferences)
    
    # Display results
    display_itinerary(trip, itinerary)

    # Display flight info if available
    if flight_info:
        print("\n" + "="*60)
        print("ESTIMATED TOTAL TRIP COST")
        print("="*60)
        total_activities = sum(sum(a.price for a in day.activities) for day in itinerary)
        total_flights = flight_info['total_price']
        print(f"Activities: ${total_activities:.2f}")
        print(f"Flights: ${total_flights:.2f}")
        print(f"TOTAL: ${total_activities + total_flights:.2f}")
    
    # Save results to file
    save = input("\nSave itinerary to file? (y/n): ").strip().lower()
    if save == 'y':
        filename = f"itinerary_{destination_slug}_{trip.start_date}.txt"
        try:
            with open(filename, 'w') as f:
                f.write(f"WANDR ITINERARY: {trip.destination}\n")
                f.write(f"Dates: {trip.start_date} to {trip.end_date}\n")
                f.write(f"Budget: ${trip.budget}\n\n")

                if flight_info:
                    f.write("FLIGHTS:\n")
                    f.write(f"  {flight_info['origin']} → {flight_info['destination']}\n")
                    f.write(f"  Price: ${flight_info['total_price']:.2f}\n")
                    f.write(f"  Departure: {flight_info['departure_date']}\n")
                    f.write(f"  Return: {flight_info.get('return_departure', 'N/A').split('T')[0]}\n\n")
                
                for i, day in enumerate(itinerary, 1):
                    f.write(f"\nDAY {i} - {day.date}\n")
                    f.write("-" * 40 + "\n")
                    for activity in day.activities:
                        f.write(f"  - {activity.name} ({activity.duration}h, ${activity.price})\n")
                        if activity.description:
                            f.write(f"    {activity.description}\n")
            
            print(f"Saved to {filename}")
        except Exception as e:
            print(f"Error saving file: {e}")
    
    print("\n✨ Thanks for using Wandr! Happy travels! ✨\n")


def main():
    """
    Main entry point - allow user to choose between GUI and CLI mode.
    """
    
    # If GUI is available, ask which mode
    if GUI_AVAILABLE:
        display_welcome()
        
        while True:
            choice = input("\nEnter choice (1-3): ").strip()
            
            if choice == '1':
                print("\nLaunching GUI...")
                gui_main()
                break
            elif choice == '2':
                print("\nStarting CLI mode...")
                run_cli_mode()
                break
            elif choice == '3':
                print("\n👋 Goodbye!")
                sys.exit(0)
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
    else:
        # No GUI available, run CLI
        print("\nGUI not available. Running CLI mode...")
        run_cli_mode()

if __name__ == "__main__":
    main()
