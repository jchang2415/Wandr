# Unit Tests for Haversine Distance Calculator

import pytest
from utils.haversine import haversine_distance_km


def test_haversine_same_location():
    '''
    Test that distance between same location is zero
    '''
    paris = (48.8566, 2.3522)
    
    distance = haversine_distance_km(paris, paris)
    
    assert distance == 0.0


def test_haversine_paris_to_london():
    '''
    Test distance between Paris and London
    Should be approximately 344 km
    '''
    paris = (48.8566, 2.3522)
    london = (51.5074, -0.1278)
    
    distance = haversine_distance_km(paris, london)
    
    # Allow 5km margin of error
    assert 340 < distance < 350


def test_haversine_nyc_to_la():
    '''
    Test distance between New York and Los Angeles
    Should be approximately 3944 km
    '''
    nyc = (40.7128, -74.0060)
    la = (34.0522, -118.2437)
    
    distance = haversine_distance_km(nyc, la)
    
    # Allow 50km margin of error for long distances
    assert 3900 < distance < 4000


def test_haversine_tokyo_to_paris():
    '''
    Test very long distance - Tokyo to Paris
    Should be approximately 9713 km
    '''
    tokyo = (35.6762, 139.6503)
    paris = (48.8566, 2.3522)
    
    distance = haversine_distance_km(tokyo, paris)
    
    # Allow 100km margin for very long distances
    assert 9600 < distance < 9800


def test_haversine_short_distance():
    '''
    Test short distance within a city
    '''
    # Eiffel Tower to Louvre Museum in Paris
    eiffel = (48.8584, 2.2945)
    louvre = (48.8606, 2.3376)
    
    distance = haversine_distance_km(eiffel, louvre)
    
    # Should be about 3.4 km
    assert 3.0 < distance < 4.0


def test_haversine_symmetry():
    '''
    Test that distance A->B equals distance B->A
    '''
    paris = (48.8566, 2.3522)
    london = (51.5074, -0.1278)
    
    distance_ab = haversine_distance_km(paris, london)
    distance_ba = haversine_distance_km(london, paris)
    
    assert distance_ab == distance_ba


def test_haversine_north_south():
    '''
    Test distance along same longitude (north-south)
    '''
    # Two points on roughly same longitude, different latitudes
    north = (45.0, 0.0)
    south = (40.0, 0.0)
    
    distance = haversine_distance_km(north, south)
    
    # 1 degree latitude ≈ 111 km, so 5 degrees ≈ 555 km
    assert 540 < distance < 570


def test_haversine_east_west():
    '''
    Test distance along same latitude (east-west)
    '''
    # Two points on equator, different longitudes
    west = (0.0, -5.0)
    east = (0.0, 5.0)
    
    distance = haversine_distance_km(west, east)
    
    # At equator, 1 degree longitude ≈ 111 km, so 10 degrees ≈ 1110 km
    assert 1100 < distance < 1120


def test_haversine_across_equator():
    '''
    Test distance crossing the equator
    '''
    north_hemisphere = (10.0, 0.0)
    south_hemisphere = (-10.0, 0.0)
    
    distance = haversine_distance_km(north_hemisphere, south_hemisphere)
    
    # 20 degrees latitude ≈ 2220 km
    assert 2200 < distance < 2250


def test_haversine_across_prime_meridian():
    '''
    Test distance crossing prime meridian (0° longitude)
    '''
    west = (51.5, -5.0)
    east = (51.5, 5.0)
    
    distance = haversine_distance_km(west, east)
    
    # At ~51° latitude, distance should be less than at equator
    assert 650 < distance < 750


def test_haversine_antipodal_points():
    '''
    Test distance between roughly antipodal points
    Should be close to half Earth's circumference
    '''
    # Madrid and roughly its antipode in Pacific
    madrid = (40.4168, -3.7038)
    antipode = (-40.4168, 176.2962)
    
    distance = haversine_distance_km(madrid, antipode)
    
    # Should be close to 20,000 km (half Earth's circumference)
    assert 19500 < distance < 20500


def test_haversine_negative_coordinates():
    '''
    Test with negative coordinates (southern/western hemispheres)
    '''
    sydney = (-33.8688, 151.2093)
    santiago = (-33.4489, -70.6693)
    
    distance = haversine_distance_km(sydney, santiago)
    
    # Approximately 11,000 km
    assert 10500 < distance < 11500


def test_haversine_near_poles():
    '''
    Test distance near the poles
    '''
    near_north_pole = (89.0, 0.0)
    near_north_pole_2 = (89.0, 90.0)
    
    distance = haversine_distance_km(near_north_pole, near_north_pole_2)
    
    # At 89° latitude, longitude circles are very small
    assert distance < 160  # Should be 157.2


def test_haversine_decimal_precision():
    '''
    Test that function handles high decimal precision
    '''
    loc1 = (48.858370, 2.294481)
    loc2 = (48.860611, 2.337644)
    
    distance = haversine_distance_km(loc1, loc2)
    
    # Eiffel Tower to Louvre - approximately 3.4 km
    assert 3.0 < distance < 4.0
    assert isinstance(distance, float)


def test_haversine_returns_positive():
    '''
    Test that distance is always positive
    '''
    paris = (48.8566, 2.3522)
    london = (51.5074, -0.1278)
    
    distance = haversine_distance_km(paris, london)
    
    assert distance > 0


def test_haversine_very_close_points():
    '''
    Test distance between very close points (meters apart)
    '''
    loc1 = (48.8584, 2.2945)
    loc2 = (48.8585, 2.2946)  # Very close to loc1
    
    distance = haversine_distance_km(loc1, loc2)
    
    # Should be less than 0.2 km (200 meters)
    assert 0 < distance < 0.2


def test_haversine_coordinate_order():
    '''
    Test that coordinate order (lat, lon) is correctly interpreted
    '''
    # Test with known distance
    paris_correct = (48.8566, 2.3522)  # lat, lon
    london_correct = (51.5074, -0.1278)
    
    distance = haversine_distance_km(paris_correct, london_correct)
    
    # Should be approximately 344 km
    assert 340 < distance < 350


def test_haversine_real_world_cities():
    '''
    Test with real-world city coordinates
    '''
    cities = {
        'Tokyo': (35.6762, 139.6503),
        'New York': (40.7128, -74.0060),
        'Paris': (48.8566, 2.3522),
        'Sydney': (-33.8688, 151.2093)
    }
    
    # Tokyo to New York should be ~10,800 km
    distance = haversine_distance_km(cities['Tokyo'], cities['New York'])
    assert 10500 < distance < 11000
    
    # Paris to Sydney should be ~17,000 km
    distance = haversine_distance_km(cities['Paris'], cities['Sydney'])

    assert 16500 < distance < 17500
