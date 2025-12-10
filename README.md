# Wandr
This respository is for Wandr, and interactive travel planner app.


## Installation
Download the zip file from the Github repository (https://github.com/jchang2415/Wandr/) and extract the contents.


## Usage
To run Wandr, open up the folder containing the downloaded repository and run the command:    
```python
python main.py
```

To use Wandr with APIs, first obtain API keys from Geoapify (https://myprojects.geoapify.com/) and Amadeus (https://developers.amadeus.com/register). Then, change the .env file in your folder to contain your API keys by replacing the relevant "your_api_key_here" instances. Finally, run the program like normal.

## Files
Wandr    
├─── api    
│       ├─── img    
│       └─── img    
├─── data    
│       ├─── img    
│       ├─── img    
│       ├─── img    
│       ├─── img    
│       └─── img  
├─── engine    
│       ├─── img    
│       └─── img  
├─── gui    
│       └─── img    
├─── models    
│       ├─── img    
│       ├─── img    
│       ├─── img    
│       └─── img    
├─── tests    
├─── utils    
│       ├─── img    
│       ├─── img    
│       └─── img   
├─── .env    
├─── LICENSE    
├─── README.md    
└─── main.py    

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

## Authors
Jason Chang

EN.540.635 Software Carpentry Johns Hopkins University, Chemical and Biomolecular Engineering Department

## Licenses
This project is licensed under the MIT License. See the license file for details.


