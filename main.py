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


def get_user_inputs():
    '''
    Function for collecting all user inputs via the command line interface.
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
    
    # Return the gathered information in a formatted dictionary
    return {
        'destination': destination,
        'start_date': start_date,
        'end_date': end_date,
        'budget': budget,
        'interests': interests,
        'schedule_type': schedule_type,
        'prioritize_cost': prioritize_cost
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
    if itinerary:
        for day, activities in itinerary.items():
            print(f"\nDay {day}:")
            for activity in activities:
                print(f"  - {activity['name']} ({activity['category']}) - ${activity['cost']:.2f}")
    else:
        print("No activities found for the selected criteria.")


def main():
    '''
    Main entry point for the travel planner.
    '''
    
    # Get user inputs
    user_inputs = get_user_inputs()
    
    # Import relevant activities from CSV data
    destination_slug = user_inputs['destination'].lower().replace(' ', '_')
    csv_path = Path(f"data/{destination_slug}_activities.csv")
    
    # Indicate if there is no data for the destination chpsen
    if not csv_path.exists():
        print(f"\n Error: No activity data available '{user_inputs['destination']}'")
        print("Please try another destination with available data.")
        return
    
    print(f"\n Loading activities from {csv_path}...")
    try:
        activities = load_activities_from_csv(csv_path)
        print(f"Loaded {len(activities)} activities")
    
    except Exception as e:
        print(f"Error loading activities: {e}")
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
    display_itinerary(user_inputs, itinerary)
    
    # Save results to file
    save = input("\nSave itinerary to file? (y/n): ").strip().lower()
    if save == 'y':
        filename = f"itinerary_{destination_slug}_{trip.start_date}.txt"
        try:
            with open(filename, 'w') as f:
                f.write(f"WANDR ITINERARY: {trip.destination}\n")
                f.write(f"Dates: {trip.start_date} to {trip.end_date}\n")
                f.write(f"Budget: ${trip.budget}\n\n")
                
                for i, day in enumerate(itinerary, 1):
                    f.write(f"\nDAY {i} - {day.date}\n")
                    f.write("-" * 40 + "\n")
                    for activity in day.activities:
                        f.write(f"  - {activity.name} ({activity.duration_hours}h, ${activity.price})\n")
                        if activity.description:
                            f.write(f"    {activity.description}\n")
            
            print(f"Saved to {filename}")
        except Exception as e:
            print(f"Error saving file: {e}")
    
    print("\n✨ Thanks for using Wandr! Happy travels! ✨\n")

if __name__ == "__main__":
    main()
