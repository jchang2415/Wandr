# Unit Tests for CSV Reader

import pytest
import tempfile
from pathlib import Path
from utils.csv_reader import load_activities_from_csv


def create_test_csv(content: str) -> Path:
    '''
    Helper function to create a temporary CSV file for testing
    '''
    temp_file = tempfile.NamedTemporaryFile(
        mode='w', delete=False, suffix='.csv', encoding='utf-8')
    temp_file.write(content)
    temp_file.close()
    return Path(temp_file.name)


def test_load_activities_basic():
    '''
    Test loading basic activities from CSV
    '''
    csv_content = """name,category,duration_hours,price,lat,lon,description
Museum,museum,2.0,15.0,41.881,-87.623,A great museum
Park,nature,1.5,0.0,41.793,-87.607,Beautiful park"""

    csv_path = create_test_csv(csv_content)

    try:
        activities = load_activities_from_csv(csv_path)

        assert len(activities) == 2
        assert activities[0].name == "Museum"
        assert activities[0].category == "museum"
        assert activities[0].duration == 2.0
        assert activities[0].price == 15.0
        assert activities[1].name == "Park"
    finally:
        csv_path.unlink()


def test_load_activities_with_missing_optional_fields():
    '''
    Test loading activities with missing optional fields
    '''
    csv_content = """name,category,duration_hours,price,lat,lon,description
Museum,museum,2.0,15.0,,,
Park,nature,1.5,0.0,41.793,-87.607,"""

    csv_path = create_test_csv(csv_content)

    try:
        activities = load_activities_from_csv(csv_path)

        assert len(activities) == 2
        assert activities[0].location is None  # Missing coordinates
        assert activities[0].description == ""  # Empty description
        assert activities[1].location == (41.793, -87.607)
        assert activities[1].description == ""
    finally:
        csv_path.unlink()


def test_load_activities_with_defaults():
    '''
    Test that default values are used when data is missing
    '''
    csv_content = """name,category,duration_hours,price,lat,lon,description
Activity,museum,,,,"""

    csv_path = create_test_csv(csv_content)

    try:
        activities = load_activities_from_csv(csv_path)

        assert len(activities) == 1
        assert activities[0].duration == 1.0  # Default
        assert activities[0].price == 0.0  # Default
        assert activities[0].location is None
        assert activities[0].description == ""
    finally:
        csv_path.unlink()


def test_load_activities_free_activity():
    '''
    Test loading free (zero price) activities
    '''
    csv_content = """name,category,duration_hours,price,lat,lon,description
Park,nature,1.0,0.0,41.793,-87.607,Free park"""

    csv_path = create_test_csv(csv_content)

    try:
        activities = load_activities_from_csv(csv_path)

        assert len(activities) == 1
        assert activities[0].price == 0.0
    finally:
        csv_path.unlink()


def test_load_activities_file_not_found():
    '''
    Test that FileNotFoundError is raised for non-existent file
    '''
    with pytest.raises(FileNotFoundError):
        load_activities_from_csv("nonexistent_file.csv")


def test_load_activities_missing_name():
    '''
    Test that ValueError is raised when activity name is missing
    '''
    csv_content = """name,category,duration_hours,price,lat,lon,description
,museum,2.0,15.0,41.881,-87.623,Missing name"""

    csv_path = create_test_csv(csv_content)

    try:
        with pytest.raises(ValueError, match="Missing activity name"):
            load_activities_from_csv(csv_path)
    finally:
        csv_path.unlink()


def test_load_activities_default_category():
    '''
    Test that default category "other" is used when missing
    '''
    csv_content = """name,category,duration_hours,price,lat,lon,description
Activity,,2.0,15.0,,,"""

    csv_path = create_test_csv(csv_content)

    try:
        activities = load_activities_from_csv(csv_path)

        assert activities[0].category == "other"
    finally:
        csv_path.unlink()


def test_load_activities_whitespace_handling():
    '''
    Test that whitespace is properly stripped from fields
    '''
    csv_content = """name,category,duration_hours,price,lat,lon,description
  Museum  ,  museum  ,2.0,15.0,,,  A great museum  """

    csv_path = create_test_csv(csv_content)

    try:
        activities = load_activities_from_csv(csv_path)

        assert activities[0].name == "Museum"
        assert activities[0].category == "museum"
        assert activities[0].description == "A great museum"
    finally:
        csv_path.unlink()


def test_load_activities_fractional_values():
    '''
    Test loading activities with fractional duration and price
    '''
    csv_content = """name,category,duration_hours,price,lat,lon,description
Tour,tour,0.5,12.50,41.881,-87.623,Quick tour"""

    csv_path = create_test_csv(csv_content)

    try:
        activities = load_activities_from_csv(csv_path)

        assert activities[0].duration == 0.5
        assert activities[0].price == 12.50
    finally:
        csv_path.unlink()


def test_load_activities_multiple_rows():
    '''
    Test loading many activities from CSV
    '''
    csv_content = """name,category,duration_hours,price,lat,lon,description
Activity1,museum,2.0,15.0,,,
Activity2,nature,1.0,0.0,,,
Activity3,food,1.5,25.0,,,
Activity4,shopping,2.5,10.0,,,
Activity5,entertainment,3.0,50.0,,,"""

    csv_path = create_test_csv(csv_content)

    try:
        activities = load_activities_from_csv(csv_path)

        assert len(activities) == 5
        assert activities[0].name == "Activity1"
        assert activities[4].name == "Activity5"
    finally:
        csv_path.unlink()


def test_load_activities_coordinates_parsing():
    '''
    Test that coordinates are correctly parsed as tuples
    '''
    csv_content = """name,category,duration_hours,price,lat,lon,description
Activity,museum,2.0,15.0,48.8584,2.2945,In Paris"""

    csv_path = create_test_csv(csv_content)

    try:
        activities = load_activities_from_csv(csv_path)

        assert activities[0].location == (48.8584, 2.2945)
        assert isinstance(activities[0].location, tuple)
    finally:
        csv_path.unlink()


def test_load_activities_invalid_coordinates():
    '''
    Test that invalid coordinates result in None location
    '''
    csv_content = """name,category,duration_hours,price,lat,lon,description
Activity,museum,2.0,15.0,invalid,invalid,Description"""

    csv_path = create_test_csv(csv_content)

    try:
        activities = load_activities_from_csv(csv_path)

        assert activities[0].location is None
    finally:
        csv_path.unlink()


def test_load_activities_partial_coordinates():
    '''
    Test that missing one coordinate results in None location
    '''
    csv_content = """name,category,duration_hours,price,lat,lon,description
Activity1,museum,2.0,15.0,48.8584,,Missing lon
Activity2,museum,2.0,15.0,,2.2945,Missing lat"""

    csv_path = create_test_csv(csv_content)

    try:
        activities = load_activities_from_csv(csv_path)

        assert activities[0].location is None
        assert activities[1].location is None
    finally:
        csv_path.unlink()


def test_load_activities_special_characters():
    '''
    Test loading activities with special characters in descriptions
    '''
    csv_content = """name,category,duration_hours,price,lat,lon,description
Café,food,1.5,20.0,,,A café with crêpes & more!"""

    csv_path = create_test_csv(csv_content)

    try:
        activities = load_activities_from_csv(csv_path)

        assert activities[0].name == "Café"
        assert "crêpes" in activities[0].description
    finally:
        csv_path.unlink()


def test_load_activities_empty_csv():
    '''
    Test loading from CSV with only headers
    '''
    csv_content = """name,category,duration_hours,price,lat,lon,description"""

    csv_path = create_test_csv(csv_content)

    try:
        activities = load_activities_from_csv(csv_path)

        assert len(activities) == 0
    finally:
        csv_path.unlink()


def test_load_activities_real_sample_format():
    '''
    Test with format matching your actual sample_data1.csv
    '''
    csv_content = """name,category,duration_hours,price,lat,lon,description
City Museum,museum,2,15,41.881,-87.623,"A contemporary city museum"
Botanical Garden,nature,3,12,41.793,-87.607,"Large garden with seasonal exhibits"
Historic District,tour,2,0,41.888,-87.626,"Walking tour of the old town"
Fine Dining,food,2.5,75,41.882,-87.620,"Upscale local cuisine"
Local Brewery,food,1.5,25,41.886,-87.617,"Brewery tour & tasting"
River Walk,nature,1,0,41.890,-87.622,"Scenic walk along the river" """

    csv_path = create_test_csv(csv_content)

    try:
        activities = load_activities_from_csv(csv_path)

        assert len(activities) == 6
        assert activities[0].name == "City Museum"
        assert activities[0].duration == 2.0
        assert activities[3].name == "Fine Dining"
        assert activities[3].price == 75.0
    finally:

        csv_path.unlink()
