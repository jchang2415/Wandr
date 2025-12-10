# Activity Lock and Itinerary Regeneration System

from typing import List, Set, Dict, Optional
from datetime import date
from models.activity import Activity
from models.dayplan import DayPlan
from models.preferences import UserPreferences
from models.trip import Trip


class ItineraryManager:
    '''
    Manages itinerary with ability to lock activities and regenerate.
    '''
    
    def __init__(self, trip: Trip, all_activities: List[Activity], prefs: UserPreferences):
        self.trip = trip
        self.all_activities = all_activities
        self.prefs = prefs
        self.current_itinerary: List[DayPlan] = []
        self.locked_activities: Set[Activity] = set()
        self.locked_per_day: Dict[date, List[Activity]] = {}  # Specific day locks
        self.excluded_activities: Set[Activity] = set()  # User doesn't want these
    
    def lock_activity(self, activity, specific_day = None):
        '''
        Lock an activity to ensure it appears in the itinerary.
        
        **Parameters**
            
            activity: *Activity*
                Activity to be locked

            specific_day: *date*
                Optional - lock it to a specific day.
                Defaults to None.
        
        **Returns**
            
            *bool*
                True if successfully locked, False otherwise
        '''
        if activity not in self.all_activities:
            print(f"❌ Activity '{activity.name}' not available")
            return False
        
        self.locked_activities.add(activity)
        
        if specific_day:
            if specific_day not in self.locked_per_day:
                self.locked_per_day[specific_day] = []
            self.locked_per_day[specific_day].append(activity)
            print(f"🔒 Locked '{activity.name}' for {specific_day}")
        else:
            print(f"🔒 Locked '{activity.name}' (will appear somewhere in itinerary)")
        
        return True
    
    def unlock_activity(self, activity):
        '''
        Remove lock from an activity.
        
        **Parameters**

            activity: *Activity*
                Activity class object to be unlocked.

        **Returns**
            *bool*
                True if successfully unlocked, False if wasn't locked
        '''
        if activity not in self.locked_activities:
            print(f"'{activity.name}' was not locked")
            return False
        
        self.locked_activities.remove(activity)
        
        # Remove from specific day locks if present
        for day, acts in self.locked_per_day.items():
            if activity in acts:
                acts.remove(activity)
        
        print(f"🔓 Unlocked '{activity.name}'")
        return True
    
    def exclude_activity(self, activity):
        '''
        Mark an activity as excluded (user doesn't want it).
        
        **Parameters**

            activity: *Activity*
                Activity class object to be unlocked.

        **Returns**

            *bool*
                True if successfully excluded
        '''
        if activity in self.locked_activities:
            print(f"Cannot exclude '{activity.name}' - it's locked")
            return False
        
        self.excluded_activities.add(activity)
        print(f"🚫 Excluded '{activity.name}' from future generations")
        return True
    
    def unexclude_activity(self, activity):
        '''
        Remove exclusion from an activity.

        **Parameters**

            activity: *Activity*
                Activity class object to be unexcluded.

        **Returns**

            *bool*
                True if successfully unexcluded
        '''
        if activity not in self.excluded_activities:
            print(f"'{activity.name}' was not excluded")
            return False
        
        self.excluded_activities.remove(activity)
        print(f"✅ '{activity.name}' is available again")
        return True
    
    def get_available_activities(self):
        '''
        Get list of activities that can be scheduled (not excluded).

        **Parameters**

            None

        **Returns**

            *list[Activity]*
        '''
        return [a for a in self.all_activities if a not in self.excluded_activities]
    
    def regenerate_itinerary(self, scheduler_func):
        '''
        Regenerate itinerary taking into account locks and exclusions.
        
        **Parameters**

            scheduler_func: *func*
                Function to create itinerary
                Should accept (trip, activities, prefs, locked_activities)
        
        **Returns**
            
            *list[DayPlan]*
                New regenerated itinerary
        '''
        available = self.get_available_activities()
        
        print(f"\n🔄 Regenerating itinerary...")
        print(f"   Available activities: {len(available)}")
        print(f"   Locked activities: {len(self.locked_activities)}")
        print(f"   Excluded activities: {len(self.excluded_activities)}")
        
        # Create new itinerary
        self.current_itinerary = scheduler_func(self.trip, available, self.prefs, list(self.locked_activities))
        
        # Verify locked activities made it in
        scheduled = set()
        for day in self.current_itinerary:
            scheduled.update(day.activities)
        
        missing_locked = self.locked_activities - scheduled
        if missing_locked:
            print(f"⚠️  Warning: Could not fit {len(missing_locked)} locked activities:")
            for act in missing_locked:
                print(f"   - {act.name} (${act.price}, {act.duration_hours}h)")
        
        return self.current_itinerary
    
    def swap_activity(self, old_activity, new_activity, day_index):
        '''
        Replace one activity with another on a specific day.
        
        **Parameters**

            old_activity: *Activity*
                Activity to remove

            new_activity: *Activity*
                Activity to add

            day_index: *int*
                Which day to work on (0-indexed)
        
        **Returns**

            *bool*
                True if swap successful
        '''
        if day_index >= len(self.current_itinerary):
            print(f"❌ Day {day_index} doesn't exist")
            return False
        
        day = self.current_itinerary[day_index]
        
        if old_activity not in day.activities:
            print(f"❌ '{old_activity.name}' not on day {day_index}")
            return False
        
        if new_activity in self.excluded_activities:
            print(f"❌ '{new_activity.name}' is excluded")
            return False
        
        # Check if new activity fits
        time_freed = old_activity.duration_hours
        if new_activity.duration_hours > time_freed:
            print(f"⚠️  '{new_activity.name}' is longer than '{old_activity.name}'")
            print(f"   May need to remove other activities")
        
        # Perform swap
        day.activities.remove(old_activity)
        day.activities.append(new_activity)
        
        print(f"✅ Swapped '{old_activity.name}' → '{new_activity.name}' on day {day_index}")
        return True
    
    def get_locked_status(self):
        '''
        Get current lock status for display.

        **Paramters**

            None

        **Returns**

            *dict*
                Dictionary containing information for all locked and excluded activities.
        '''
        return {
            'locked_count': len(self.locked_activities),
            'locked_activities': list(self.locked_activities),
            'excluded_count': len(self.excluded_activities),
            'excluded_activities': list(self.excluded_activities),
            'day_specific_locks': {
                day: [a.name for a in acts] 
                for day, acts in self.locked_per_day.items()
            }
        }
    
    def save_itinerary_state(self, filename):
        '''
        Save current itinerary with locks to a file.

        **Parameters**

            filename: *str*
                File name to save the itinerary state to.

        **Returns**

            None
        '''
        import json
        
        state = {
            'destination': self.trip.destination,
            'start_date': self.trip.start_date.isoformat(),
            'end_date': self.trip.end_date.isoformat(),
            'locked_activities': [a.name for a in self.locked_activities],
            'excluded_activities': [a.name for a in self.excluded_activities],
            'itinerary': [
                {
                    'date': day.date.isoformat(),
                    'activities': [a.name for a in day.activities]
                }
                for day in self.current_itinerary
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"Saved itinerary state to {filename}")


def interactive_refinement_cli(manager, scheduler_func):
    '''
    Interactive CLI for refining itinerary with locks and regeneration.
    
    **Parameters**

        manager: *ItineraryManager*
            Itinerary Manager instance

        scheduler_func: *func*
            Scheduling function to use

    **Returns**

        None
    '''
    
    # Generate initial itinerary
    manager.regenerate_itinerary(scheduler_func)
    
    while True:
        print("\n" + "="*60)
        print("ITINERARY REFINEMENT MENU")
        print("="*60)
        print("1. View current itinerary")
        print("2. Lock an activity")
        print("3. Unlock an activity")
        print("4. Exclude an activity (don't want it)")
        print("5. Unexclude an activity")
        print("6. Regenerate itinerary")
        print("7. View lock status")
        print("8. Save and finish")
        print("9. Exit without saving")
        
        choice = input("\nChoose option (1-9): ").strip()
        
        if choice == '1':
            # Display itinerary
            for i, day in enumerate(manager.current_itinerary):
                print(f"\n📅 Day {i+1} - {day.date}")
                for j, act in enumerate(day.activities, 1):
                    locked = "🔒" if act in manager.locked_activities else ""
                    print(f"   {j}. {act.name} {locked} ({act.duration_hours}h, ${act.price})")
        
        elif choice == '2':
            # Lock activity
            activity_name = input("Enter activity name to lock: ").strip()
            activity = next((a for a in manager.all_activities if a.name.lower() == activity_name.lower()), None)
            if activity:
                manager.lock_activity(activity)
            else:
                print(f"❌ Activity '{activity_name}' not found")
        
        elif choice == '3':
            # Unlock activity
            activity_name = input("Enter activity name to unlock: ").strip()
            activity = next((a for a in manager.locked_activities if a.name.lower() == activity_name.lower()), None)
            if activity:
                manager.unlock_activity(activity)
            else:
                print(f"❌ Activity '{activity_name}' not locked")
        
        elif choice == '4':
            # Exclude activity
            activity_name = input("Enter activity name to exclude: ").strip()
            activity = next((a for a in manager.all_activities if a.name.lower() == activity_name.lower()), None)
            if activity:
                manager.exclude_activity(activity)
            else:
                print(f"❌ Activity '{activity_name}' not found")
        
        elif choice == '5':
            # Unexclude
            activity_name = input("Enter activity name to unexclude: ").strip()
            activity = next((a for a in manager.excluded_activities if a.name.lower() == activity_name.lower()), None)
            if activity:
                manager.unexclude_activity(activity)
            else:
                print(f"❌ Activity '{activity_name}' not excluded")
        
        elif choice == '6':
            # Regenerate
            manager.regenerate_itinerary(scheduler_func)
            print("✅ Itinerary regenerated!")
        
        elif choice == '7':
            # Show status
            status = manager.get_locked_status()
            print(f"\n🔒 Locked: {status['locked_count']}")
            for act in status['locked_activities']:
                print(f"   - {act.name}")
            print(f"\n🚫 Excluded: {status['excluded_count']}")
            for act in status['excluded_activities']:
                print(f"   - {act.name}")
        
        elif choice == '8':
            # Save and exit
            filename = f"itinerary_{manager.trip.destination}_{manager.trip.start_date}.json"
            manager.save_itinerary_state(filename)
            print("👋 Goodbye!")
            break
        
        elif choice == '9':
            # Exit without saving
            print("👋 Exiting without saving...")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-9.")