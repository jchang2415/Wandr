# Code for GUI #
'''
Wandr GUI code using TKinter 
'''

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import date, datetime, timedelta
from typing import List, Optional
import threading

# Import modules
from models.activity import Activity
from models.preferences import UserPreferences
from models.trip import Trip
from engine.scheduler import create_itinerary
from api.geoapify_api import fetch_activities_for_city, get_comprehensive_activities

# Import flight API
try:
    from api.amadeus_api import AmadeusFlightAPI, search_trip_flights
    FLIGHT_API_AVAILABLE = True
except ImportError:
    FLIGHT_API_AVAILABLE = False

class WandrGUI:
    '''
    Main GUI application for Wandr travel planner.
    '''
    
    def __init__(self, root):
        self.root = root
        self.root.title("Wandr - Your Travel Planner")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Configure colors
        self.bg_color = "#f0f4f8"
        self.primary_color = "#2563eb"
        self.secondary_color = "#64748b"
        self.accent_color = "#10b981"
        
        self.root.configure(bg=self.bg_color)
        
        # Store data
        self.activities: List[Activity] = []
        self.trip: Optional[Trip] = None
        self.preferences: Optional[UserPreferences] = None
        self.itinerary = []
        self.flight_info = None
        
        # Create UI
        self.create_widgets()
    
    def create_widgets(self):
        '''
        Create all GUI widgets.
        '''
        
        # Header
        header_frame = tk.Frame(self.root, bg=self.primary_color, height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="✈️ WANDR",
            font=("Arial", 28, "bold"),
            bg=self.primary_color,
            fg="white"
        )
        title_label.pack(pady=20)
        
        # Main container with notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_input_tab()
        self.create_results_tab()
        
        # Status bar at bottom
        self.status_bar = tk.Label(
            self.root,
            text="Ready to plan your trip!",
            bg=self.secondary_color,
            fg="white",
            font=("Arial", 9),
            anchor=tk.W,
            padx=10
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_input_tab(self):
        '''
        Create the input form tab.
        '''
        input_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(input_frame, text="  Plan Trip  ")
        
        # Create scrollable canvas
        canvas = tk.Canvas(input_frame, bg=self.bg_color)
        scrollbar = ttk.Scrollbar(input_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Content
        content = scrollable_frame
        padding = 20
        
        # Flight Search Section
        if FLIGHT_API_AVAILABLE:
            self.create_section_header(content, "✈️ Flight Search (Optional)", padding)
            
            flight_frame = tk.Frame(content, bg=self.bg_color)
            flight_frame.pack(pady=5, padx=padding, fill=tk.X)
            
            self.search_flights_var = tk.BooleanVar()
            tk.Checkbutton(
                flight_frame,
                text="Include flight search",
                variable=self.search_flights_var,
                bg=self.bg_color,
                font=("Arial", 10),
                activebackground=self.bg_color,
                command=self.toggle_flight_fields
            ).pack(anchor=tk.W, pady=5)
            
            self.origin_frame = tk.Frame(flight_frame, bg=self.bg_color)
            self.origin_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(
                self.origin_frame,
                text="Departure City:",
                bg=self.bg_color,
                font=("Arial", 10)
            ).pack(side=tk.LEFT)
            
            self.origin_var = tk.StringVar()
            self.origin_entry = tk.Entry(
                self.origin_frame,
                textvariable=self.origin_var,
                font=("Arial", 10),
                width=20,
                state=tk.DISABLED
            )
            self.origin_entry.pack(side=tk.LEFT, padx=10)
            
            tk.Label(
                self.origin_frame,
                text="(e.g., New York, Paris)",
                bg=self.bg_color,
                font=("Arial", 8),
                fg=self.secondary_color
            ).pack(side=tk.LEFT)
        
        # Destination
        self.create_section_header(content, "📍 Destination", padding)
        self.destination_var = tk.StringVar()
        self.create_entry(content, "City:", self.destination_var, padding)
        
        # Dates
        self.create_section_header(content, "📅 Travel Dates", padding)
        
        date_frame = tk.Frame(content, bg=self.bg_color)
        date_frame.pack(pady=5, padx=padding, fill=tk.X)
        
        # Start date
        tk.Label(date_frame, text="Start Date:", bg=self.bg_color, font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.start_date_var = tk.StringVar(value=date.today().isoformat())
        tk.Entry(date_frame, textvariable=self.start_date_var, width=15, font=("Arial", 10)).grid(row=0, column=1, sticky=tk.W, padx=10)
        tk.Label(date_frame, text="(YYYY-MM-DD)", bg=self.bg_color, font=("Arial", 8), fg=self.secondary_color).grid(row=0, column=2, sticky=tk.W)
        
        # End date
        tk.Label(date_frame, text="End Date:", bg=self.bg_color, font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        default_end = (date.today() + timedelta(days=7)).isoformat()
        self.end_date_var = tk.StringVar(value=default_end)
        tk.Entry(date_frame, textvariable=self.end_date_var, width=15, font=("Arial", 10)).grid(row=1, column=1, sticky=tk.W, padx=10)
        tk.Label(date_frame, text="(YYYY-MM-DD)", bg=self.bg_color, font=("Arial", 8), fg=self.secondary_color).grid(row=1, column=2, sticky=tk.W)
        
        # Budget
        self.create_section_header(content, "💰 Budget", padding)
        self.budget_var = tk.StringVar(value="500")
        self.create_entry(content, "Total Budget (USD):", self.budget_var, padding)
        
        # Interests
        self.create_section_header(content, "❤️ Interests", padding)
        
        interests_frame = tk.Frame(content, bg=self.bg_color)
        interests_frame.pack(pady=5, padx=padding, fill=tk.X)
        
        self.interest_vars = {}
        interests = ["museum", "nature", "food", "shopping", "entertainment", "landmark", "tour"]
        
        for i, interest in enumerate(interests):
            var = tk.BooleanVar(value=(interest in ["museum", "food", "nature"]))  # Default selections
            self.interest_vars[interest] = var
            cb = tk.Checkbutton(
                interests_frame,
                text=interest.capitalize(),
                variable=var,
                bg=self.bg_color,
                font=("Arial", 10),
                activebackground=self.bg_color
            )
            cb.grid(row=i//3, column=i%3, sticky=tk.W, padx=10, pady=5)
        
        # Schedule Type
        self.create_section_header(content, "⏰ Schedule Type", padding)
        
        schedule_frame = tk.Frame(content, bg=self.bg_color)
        schedule_frame.pack(pady=5, padx=padding, fill=tk.X)
        
        self.schedule_var = tk.StringVar(value="balanced")
        
        schedules = [
            ("Relaxed (2-3 activities/day)", "relaxed"),
            ("Balanced (3-4 activities/day)", "balanced"),
            ("Packed (5+ activities/day)", "packed")
        ]
        
        for text, value in schedules:
            rb = tk.Radiobutton(
                schedule_frame,
                text=text,
                variable=self.schedule_var,
                value=value,
                bg=self.bg_color,
                font=("Arial", 10),
                activebackground=self.bg_color
            )
            rb.pack(anchor=tk.W, pady=2)
        
        # Preferences
        self.create_section_header(content, "⚙️ Preferences", padding)
        
        pref_frame = tk.Frame(content, bg=self.bg_color)
        pref_frame.pack(pady=5, padx=padding, fill=tk.X)
        
        self.prioritize_cost_var = tk.BooleanVar()
        tk.Checkbutton(
            pref_frame,
            text="Prioritize cheaper activities",
            variable=self.prioritize_cost_var,
            bg=self.bg_color,
            font=("Arial", 10),
            activebackground=self.bg_color
        ).pack(anchor=tk.W, pady=2)
        
        self.prioritize_distance_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            pref_frame,
            text="Minimize travel between activities",
            variable=self.prioritize_distance_var,
            bg=self.bg_color,
            font=("Arial", 10),
            activebackground=self.bg_color
        ).pack(anchor=tk.W, pady=2)
        
        # Generate button
        button_frame = tk.Frame(content, bg=self.bg_color)
        button_frame.pack(pady=30)
        
        self.generate_btn = tk.Button(
            button_frame,
            text="🎉 Generate Itinerary",
            command=self.generate_itinerary,
            bg=self.primary_color,
            fg="white",
            font=("Arial", 14, "bold"),
            padx=30,
            pady=15,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.generate_btn.pack()

    
    def toggle_flight_fields(self):
        """Enable/disable flight search fields based on checkbox."""
        if self.search_flights_var.get():
            self.origin_entry.config(state=tk.NORMAL)
        else:
            self.origin_entry.config(state=tk.DISABLED)
            self.origin_var.set("")
            
    
    def create_results_tab(self):
        '''Create the results display tab.'''
        results_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(results_frame, text="  Your Itinerary  ")
        
        # Toolbar
        toolbar = tk.Frame(results_frame, bg=self.bg_color)
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            toolbar,
            text="💾 Save to File",
            command=self.save_itinerary,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=5,
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="🔄 Regenerate",
            command=self.generate_itinerary,
            bg=self.secondary_color,
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=5,
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=5)
        
        # Results display
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="white",
            relief=tk.FLAT,
            padx=15,
            pady=15
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Configure text tags for styling
        self.results_text.tag_config("header", font=("Arial", 16, "bold"), foreground=self.primary_color)
        self.results_text.tag_config("day_header", font=("Arial", 13, "bold"), foreground=self.accent_color)
        self.results_text.tag_config("activity", font=("Arial", 11))
        self.results_text.tag_config("detail", font=("Arial", 9), foreground=self.secondary_color)
        self.results_text.tag_config("flight", font=("Arial", 11, "bold"), foreground="#e67e22")
    
    def create_section_header(self, parent, text, padding):
        '''
        Create a section header.
        '''
        label = tk.Label(
            parent,
            text=text,
            bg=self.bg_color,
            font=("Arial", 13, "bold"),
            fg=self.primary_color,
            anchor=tk.W
        )
        label.pack(pady=(15, 5), padx=padding, fill=tk.X)
    
    def create_entry(self, parent, label_text, variable, padding):
        '''
        Create a labeled entry field.
        '''
        frame = tk.Frame(parent, bg=self.bg_color)
        frame.pack(pady=5, padx=padding, fill=tk.X)
        
        tk.Label(frame, text=label_text, bg=self.bg_color, font=("Arial", 10), width=20, anchor=tk.W).pack(side=tk.LEFT)
        entry = tk.Entry(frame, textvariable=variable, font=("Arial", 10), width=30)
        entry.pack(side=tk.LEFT, padx=10)
    
    def update_status(self, message):
        '''
        Update status bar message.
        '''
        self.status_bar.config(text=message)
        self.root.update()
    
    def validate_inputs(self) -> bool:
        '''
        Validate user inputs.
        '''
        # Check destination
        if not self.destination_var.get().strip():
            messagebox.showerror("Error", "Please enter a destination city.")
            return False
        
        # Check dates
        try:
            start = date.fromisoformat(self.start_date_var.get())
            end = date.fromisoformat(self.end_date_var.get())
            if end < start:
                messagebox.showerror("Error", "End date must be after start date.")
                return False
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
            return False
        
        # Check budget
        try:
            budget = float(self.budget_var.get())
            if budget <= 0:
                messagebox.showerror("Error", "Budget must be positive.")
                return False
        except ValueError:
            messagebox.showerror("Error", "Invalid budget amount.")
            return False
        
        # Check at least one interest selected
        if not any(var.get() for var in self.interest_vars.values()):
            messagebox.showerror("Error", "Please select at least one interest.")
            return False

        # Check origin if flight search enabled
        if FLIGHT_API_AVAILABLE and self.search_flights_var.get():
            if not self.origin_var.get().strip():
                messagebox.showerror("Error", "Please enter departure city for flight search.")
                return False
        
        return True
    
    def generate_itinerary(self):
        '''
        Generate the travel itinerary.
        '''
        if not self.validate_inputs():
            return
        
        # Disable button during generation
        self.generate_btn.config(state=tk.DISABLED, text="⏳ Generating...")
        self.update_status("Generating itinerary...")
        
        # Run in separate thread to keep UI responsive
        thread = threading.Thread(target=self._generate_itinerary_thread)
        thread.daemon = True
        thread.start()
    
    def _generate_itinerary_thread(self):
        '''
        Background thread for itinerary generation.
        '''
        try:
            # Collect inputs
            destination = self.destination_var.get().strip()
            start_date = date.fromisoformat(self.start_date_var.get())
            end_date = date.fromisoformat(self.end_date_var.get())
            budget = float(self.budget_var.get())
            
            interests = [interest for interest, var in self.interest_vars.items() if var.get()]
            schedule_type = self.schedule_var.get()
            prioritize_cost = self.prioritize_cost_var.get()
            prioritize_distance = self.prioritize_distance_var.get()

            # Search for flights if enabled
            self.flight_info = None
            if FLIGHT_API_AVAILABLE and self.search_flights_var.get():
                origin = self.origin_var.get().strip()
                self.root.after(0, lambda: self.update_status(f"Searching for flights from {origin}..."))
                
                try:
                    self.flight_info = search_trip_flights(origin, destination, start_date, end_date)
                except Exception as e:
                    print(f"Flight search error: {e}")
            
            # Fetch activities from API
            self.root.after(0, lambda: self.update_status(f"Fetching activities for {destination}..."))
            
            try:
                self.activities = get_comprehensive_activities(destination, total_limit=60)
            except Exception as e:
                # Fallback to basic fetch
                self.activities = fetch_activities_for_city(destination, limit=50)
            
            if not self.activities:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Could not find activities for '{destination}'. Please check the city name."))
                self.root.after(0, lambda: self.generate_btn.config(state=tk.NORMAL, text="🎉 Generate Itinerary"))
                return
            
            # Create trip and preferences
            self.trip = Trip(
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                budget=budget,
                interests=interests
            )
            
            self.preferences = UserPreferences(
                interests=interests,
                budget=budget,
                schedule_type=schedule_type,
                prioritize_cost=prioritize_cost,
                prioritize_distance=prioritize_distance
            )
            
            # Generate itinerary
            self.root.after(0, lambda: self.update_status("Building your itinerary..."))
            self.itinerary = create_itinerary(self.trip, self.activities, self.preferences)
            
            # Display results
            self.root.after(0, self.display_results)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.generate_btn.config(state=tk.NORMAL, text="🎉 Generate Itinerary"))
            self.root.after(0, lambda: self.update_status("Itinerary generated!"))
    
    def display_results(self):
        '''
        Display the generated itinerary.
        '''
        self.results_text.delete(1.0, tk.END)
        
        # Header
        self.results_text.insert(tk.END, f"✈️  {self.trip.destination.upper()} ITINERARY\n\n", "header")
        self.results_text.insert(tk.END, f"📅 Dates: {self.trip.start_date} to {self.trip.end_date}\n")
        self.results_text.insert(tk.END, f"💰 Budget: ${self.trip.budget}\n")
        self.results_text.insert(tk.END, f"🗓️  Trip Length: {self.trip.trip_length()} days\n")
        
        # Display flight info if available
        if self.flight_info:
            self.results_text.insert(tk.END, "\n" + "="*70 + "\n", "header")
            self.results_text.insert(tk.END, "✈️  FLIGHT INFORMATION\n", "flight")
            self.results_text.insert(tk.END, "="*70 + "\n")
            self.results_text.insert(tk.END, f"Route: {self.flight_info['origin']} → {self.flight_info['destination']}\n", "detail")
            self.results_text.insert(tk.END, f"Price: ${self.flight_info['total_price']:.2f} {self.flight_info['currency']}\n", "detail")
            self.results_text.insert(tk.END, f"Departure: {self.flight_info['departure_date']} at {self.flight_info.get('departure_time', '')[:5]}\n", "detail")
            self.results_text.insert(tk.END, f"Duration: {self.flight_info['duration']}\n", "detail")
            self.results_text.insert(tk.END, f"Stops: {self.flight_info['stops']}\n", "detail")
            self.results_text.insert(tk.END, f"Airline: {self.flight_info['airline']}\n", "detail")
        
        self.results_text.insert(tk.END, "=" * 70 + "\n\n")
        
        # Itinerary by day
        total_cost = 0
        for i, day in enumerate(self.itinerary, 1):
            day_cost = sum(a.price for a in day.activities)
            total_cost += day_cost
            
            self.results_text.insert(tk.END, f"DAY {i} - {day.date}\n", "day_header")
            self.results_text.insert(tk.END, f"Total: {day.total_duration():.1f} hours, ${day_cost:.2f}\n", "detail")
            self.results_text.insert(tk.END, "-" * 70 + "\n")
            
            if not day.activities:
                self.results_text.insert(tk.END, "   No activities scheduled\n\n")
            else:
                for j, activity in enumerate(day.activities, 1):
                    self.results_text.insert(tk.END, f"\n{j}. {activity.name}\n", "activity")
                    self.results_text.insert(tk.END, 
                        f"   {activity.category} | {activity.duration_hours}h | ${activity.price}\n",
                        "detail")
                    if activity.description:
                        desc = activity.description[:100] + "..." if len(activity.description) > 100 else activity.description
                        self.results_text.insert(tk.END, f"   {desc}\n", "detail")
            
            self.results_text.insert(tk.END, "\n")
        
        # Summary
        self.results_text.insert(tk.END, "=" * 70 + "\n", "header")

        if self.flight_info:
            flight_cost = self.flight_info['total_price']
            self.results_text.insert(tk.END, f"\nACTIVITIES COST: ${total_cost:.2f}\n", "activity")
            self.results_text.insert(tk.END, f"FLIGHTS COST: ${flight_cost:.2f}\n", "flight")
            self.results_text.insert(tk.END, f"TOTAL TRIP COST: ${total_cost + flight_cost:.2f}\n", "header")
        else:
            self.results_text.insert(tk.END, f"\nTOTAL ACTIVITIES COST: ${total_cost:.2f} / ${self.trip.budget:.2f}\n", "header")
        
        if total_cost <= self.trip.budget:
            remaining = self.trip.budget - total_cost
            self.results_text.insert(tk.END, f"✅ Within budget! (${remaining:.2f} remaining)\n", "activity")
        else:
            over = total_cost - self.trip.budget
            self.results_text.insert(tk.END, f"⚠️  Over budget by ${over:.2f}\n", "detail")
        
        # Switch to results tab
        self.notebook.select(1)
    
    def save_itinerary(self):
        '''
        Save itinerary to a file.
        '''
        if not self.itinerary:
            messagebox.showwarning("Warning", "No itinerary to save. Please generate one first.")
            return
        
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"itinerary_{self.trip.destination}_{self.trip.start_date}.txt"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Itinerary saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")


def main():
    '''
    Launch the GUI application.
    '''
    root = tk.Tk()
    app = WandrGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
