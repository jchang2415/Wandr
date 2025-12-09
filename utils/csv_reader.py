# CSV Loader
'''
Code for reading in a CSV file containing the information about the things to do in a location
and parsing it into Activity class objects.
'''

import csv
from typing import List, Optional
from pathlib import Path

from models.activity import Activity

# Define helper method for preventing errors on processing floats
def _safe_float(value: Optional[str], default: float = 0.0) -> float:
    '''
    Convert string to float safely, return default on empty or bad input.
    '''
    if value is None or value == "":
        return default
    try:
        return float(value)
    except ValueError:
        return default

# Define a helper method for correctly parsing in latitude and longitude data
def _safe_coord(lat: Optional[str], lon: Optional[str]) -> Optional[tuple]:
    '''
    Convert lat/lon strings to a (lat, lon) tuple or return None if coordinates
    are missing/invalid.
    '''
    if lat in (None, "") or lon in (None, ""):
        return None
    try:
        return (float(lat), float(lon))
    except ValueError:
        return None

# Define method for parsing activity data from input csv
def load_activities_from_csv(path: str | Path) -> List[Activity]:
    '''
    Read activities from a CSV file and return a list of Activity objects.

    Expected CSV columns (header row):
    name, category, duration_hours, price, lat, lon, description

    Only 'name', 'category', 'duration_hours' and 'price' are required
    logically — others are optional.
    '''
    # Initialize empty activities class object to store parsed data
    activities: List[Activity] = []

    # Get path of CSV
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    # Open the file at the filepath given
    with path.open(newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        # Read the file row by row and parse data by the different types of information about an activity
        for i, row in enumerate(reader, start=1):
            
            # Require basic information of name and category for an activity
            name = row.get("name", "").strip()
            category = row.get("category", "").strip() or "other"

            # Use "safe" method in case duration or pricing information is missing
            duration = _safe_float(row.get("duration_hours"), default=1.0)
            price = _safe_float(row.get("price"), default=0.0)

            # Use "safe" method in case location or description information is missing
            location = _safe_coord(row.get("lat"), row.get("lon"))
            description = row.get("description", "").strip()

            # Skip rows without a name
            if not name:
                
                raise ValueError(f"Missing activity name in CSV row {i}: {row}")

            # Create an Activity class object with the parsed information from that row
            activity = Activity(
                name=name,
                category=category,
                duration_hours=duration,
                price=price,
                location=location,
                description=description
            )

            # Add the activity from the row to the list of activities
            activities.append(activity)

    # Return the parsed list of all activities in the input file
    return activities