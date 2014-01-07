'''
Module with static utility functions for calculating geocells and operating on
them.
Created on Dec 5, 2013

@author: diegob
'''

import math

###################
# Limits          #
###################
MIN_LATITUDE = -90.0
MIN_LONGITUDE = -180.0
MAX_LATITUDE = 90.0
MAX_LONGITUDE = 180.0
RADIUS = 6378137.0  # In m

###################
# Geocell mapping #
# +---+---+---+---+
# | a | b | e | f |
# +---+---+---+---+
# | 8 | 9 | c | d |
# +---+---+---+---+
# | 2 | 3 | 6 | 7 |
# +---+---+---+---+
# | 0 | 1 | 4 | 5 |
# +---+---+---+---+
###################
GRID_SIZE = 4
GEO_MAPPING = {(0, 0) : '0',
               (0, 1) : '1',
               (1, 0) : '2',
               (1, 1) : '3',
               (0, 2) : '4',
               (0, 3) : '5',
               (1, 2) : '6',
               (1, 3) : '7',
               (2, 0) : '8',
               (2, 1) : '9',
               (3, 0) : 'a',
               (3, 1) : 'b',
               (2, 2) : 'c',
               (2, 3) : 'd',
               (3, 2) : 'e',
               (3, 3) : 'f'}

def computegeocell(point):
    '''
    Compute a geocell for the given geopoint with the maximum resolution,
    the mapping from cells to characters is given by GEO_MAPPING. Additionally,
    this uses the constant GRID_SIZE and the limits defined above for
    latitude and longitude.
    '''
    # Define the initial bounding box (the whole world)
    south = MIN_LATITUDE
    north = MAX_LATITUDE
    west = MIN_LONGITUDE
    east = MAX_LONGITUDE
    #raise Exception("%s, %s" % (point.latitude, point.longitude))
    geocell_list = []
    resolution = point.resolution
    while(resolution > 0):
        # Find the new cell
        x_cell = int(min((point.latitude - south) * GRID_SIZE / (north - south), GRID_SIZE - 1))
        y_cell = int(min((point.longitude - west) * GRID_SIZE / (east - west), GRID_SIZE - 1))

        # Zoom into the cell
        south += x_cell * (north - south) / 4
        north -= ((GRID_SIZE - 1) - x_cell) * (north - south) / 4
        west += y_cell * (east - west) / 4
        east -= ((GRID_SIZE - 1) - y_cell) * (east - west) / 4

        # Find the char for the cell and advance
        cell_char = GEO_MAPPING[(x_cell, y_cell)]
        geocell_list.append(cell_char)
        resolution -= 1

    geocell = ''.join(geocell_list)
    return geocell

def distance(point_1, point_2):
    '''
    Utility function to calculate the great-circle distance between two points.
    
    It uses the formula derived from the Vicenty formula which is expected
    to be more well behaved in numeric terms.

    The distance is returned in meters.
    '''

    # Calculate the angles
    phi_1 = math.radians(point_1.latitude)
    phi_2 = math.radians(point_2.latitude)
    lambda_1 = math.radians(point_1.longitude)
    lambda_2 = math.radians(point_2.longitude)
    delta_lambda = abs(lambda_2 - lambda_1)

    # Calculate the parts of the equation
    numerator = (math.cos(phi_2) * math.sin(delta_lambda)) ** 2 + \
                (math.cos(phi_1) * math.sin(phi_2) -
                 math.sin(phi_1) * math.cos(phi_2) * math.cos(delta_lambda)) ** 2
    denominator = math.sin(phi_1) * math.sin(phi_2) + \
                  math.cos(phi_1) * math.cos(phi_2) * math.cos(delta_lambda)

    # Get the arc length, i.e. the great-circle distance
    result = RADIUS * (math.atan2(math.sqrt(numerator), denominator))
    return result

def simple_search(center, stored_points, max_results = 10, max_distance = 1000.0):
    '''
    Simple search algorithm on geocells, given a center GeoPoint and a list
    of other GeoPoint objects. The algorithm finds a number of closest points
    given a max_distance and a maximum number of points to return.

    The algorithms works by examining the parent cells of the central point, 
    it runs on O(res*nlog(n)) where n is the number of points in stored_points
    and res is the maximum resolution of the geocells.
    
    Pre: All points in stored_points have the same max resolution as the central
    point.
    '''
    results = set()
    max_resolution = center.resolution
    while len(results) < max_results and max_resolution >= 0:
        partial_results = []
        cell_of_interest = center.max_geocell[:max_resolution]
        for interest_point in stored_points:
            if(interest_point.max_geocell.startswith(cell_of_interest)):
                partial_results.append(interest_point)
        partial_results = filter(lambda x: distance(x, center) < max_distance, partial_results)
        partial_results.sort(key = lambda x: distance(x, center))
        partial_results = partial_results[:max_results]
        results = results.union(set(partial_results))
        max_resolution -= 1
    return (list(results))[:max_results]
