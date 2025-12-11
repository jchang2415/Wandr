# Wandr
This respository is for Wandr, and interactive travel planner app. Wandr helps create a personalized itinerary for you (cheapest flight available included!) for your indicated destination, interests, and travel preferences.

<img width="1120" height="908" alt="image" src="https://github.com/user-attachments/assets/b6996392-4074-4d59-b5bf-6782c8de7905" />


## Installation
Download the zip file from the Github repository (https://github.com/jchang2415/Wandr/) and extract the contents.    
    
Must also have dependencies installed:
- requests>=2.31.0
- python-dotenv>=1.0.0
- amadeus>=9.0.0


## Usage
To run Wandr, open up the folder containing the downloaded repository and run the command:    
```python
python main.py
```

You must use the command line interface for the first step. When prompted, select whether to proceed with:
- Option 1: GUI - Graphical interface (recommended)
- Option 2: CLI - Command-line interface (for advanced users or testing)

To use Wandr with APIs, first obtain API keys from Geoapify (https://myprojects.geoapify.com/) and Amadeus (https://developers.amadeus.com/register). Then, change the .env file in your folder to contain your API keys by replacing the relevant "your_api_key_here" instances. Finally, run the program like normal.     

See sample_output.txt file in data/ for an example of output file from Wandr.
<img width="808" height="731" alt="image" src="https://github.com/user-attachments/assets/0e0ecfc6-5a03-4a69-84d5-d4825dd981cf" />


## Files
File structure:
```
Wandr    
├─── api    
│     ├─── amadeus_api.py    
│     └─── geoapify_api.py    
├─── data    
│     └─── ...    
├─── engine    
│     ├─── scheduler.py    
│     └─── scorer.py  
├─── gui    
│     └─── gui.py    
├─── models    
│     ├─── activity.py    
│     ├─── dayplan.py    
│     ├─── trip.py    
│     └─── preferences.py    
├─── tests     
│     └─── ...        
├─── utils    
│     ├─── csv_reader.py    
│     ├─── haversine.py    
│     └─── editor.py   
├─── .env    
├─── LICENSE    
├─── README.md    
└─── main.py
```   

File Explanations
- *api/*:  contains code for integrating the program with external APIs (Geoapify for Point of Interest information, Amadeus for Flight information)
- *data/*: contains csv files containing sample input activity data for use without APIs / demos and information on airport IATA codes
- *engine/*: contains main "algorithm" files of program that calculate score for each available activity based on indicated user preferences and intelligently organizes them into geographically clustered schedules across days
- *gui/*: contains code encoding the graphical user interface
- *models/*: contains code defining classes (Activity, DayPlan, Trip, UserPreferences) for easier interaction of program with the data
- *tests/*: contains various unit tests for each of our codes (except for APIs and GUI)
- *utils/*: contains miscallaneous helper functions for parsing CSVs, editing itineraries, and calculating geographic distance
- *.env*: file required for API use; must obtain own API keys and replace this code with your specific API codes for API aspect to work!
- *main.py*: main file that serves as entry point for program and integrates all other code

## Features
- Generates an itinerary based on your indicated trip dates, destination, and budget
- Integrates APIs to get live flight pricing information and Point of Interest information
- Retrieves the cheapest flight from your city of origin to the destination
- Takes in user preferences (cost preferences, travel style, interests) to customize your itinerary
- Saves your itinerary to an output .txt file

## Running Unit Tests
To run unit tests, make sure pytest is installed. If not installed, install it using:
    
```pip install pytest```

Then run the unit tests using this command:

```python -m pytest -v```

Example Output:
<img width="1167" height="507" alt="image" src="https://github.com/user-attachments/assets/42ee5cf9-9fab-46c2-9b5f-6aed0041ca9a" />
<img width="1167" height="522" alt="image" src="https://github.com/user-attachments/assets/1fa47597-6bd4-4411-a422-6f86030523f3" />


## Authors
Jason Chang

EN.540.635 Software Carpentry Johns Hopkins University, Chemical and Biomolecular Engineering Department

## Licenses
This project is licensed under the MIT License. See the license file for details.


