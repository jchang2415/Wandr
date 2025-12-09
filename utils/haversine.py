# Geographic Distance Calculator (Haversine Method)

from math import radians, sin, cos, sqrt, atan2

def haversine_distance_km(a, b):
    """
    Compute the great-circle distance between two points in kilometers using
    the Haversine formula. Inputs are (lat, lon) pairs in decimal degrees.

    **Parameters**

        a: *Tuple(float, float)*
            The latitude and longitude coordinates of the first location.

        b: *Tuple(float, float)*
            The latitude and longitude coordinates of the second location.

    **Returns**

        distance: *float*
            The calculated Haversine distance between the two points in kilometers.

    """
    # Parse out latitude and longitude coordinates from inputs
    lat1, lon1 = a
    lat2, lon2 = b

    # convert decimal degrees to radians
    rlat1, rlon1, rlat2, rlon2 = map(radians, (lat1, lon1, lat2, lon2))

    # Calculate latitudinal distance
    dlat = rlat2 - rlat1

    # Calculate longitudinal distance
    dlon = rlon2 - rlon1

    # Define Earth's radius in kilometers
    R = 6371.0 

    # Apply Haversine formula
    h = sin(dlat / 2) ** 2 + (cos(rlat1) * cos(rlat2) * sin(dlon / 2) ** 2)
    distance = 2 * R * atan2(sqrt(h), sqrt(1 - h))

    # Return calculated distance
    return distance