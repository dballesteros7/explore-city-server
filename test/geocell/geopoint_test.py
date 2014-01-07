'''
Test module for the geopoint and utils modules.
Created on Dec 5, 2013

@author: diegob
'''
import unittest

from geocell import utils
from geocell.geopoint import GeoPoint

class GeoPointTest(unittest.TestCase):
    '''
    Check the basic functionality of the GeoPoint class, this also
    checks the sanity of the utils functions relating to GeoPoint objects.
    '''

    def test_creation(self):
        x = GeoPoint(7.1333, -73.0000)
        print x.max_geocell

    def test_distance(self):
        x_1 = GeoPoint(7.1333, -73.0000) # Bucaramanga
        x_2 = GeoPoint(7.1233, -73.0000) # Some other point
        x_3 = GeoPoint(47.3667, 8.5500) # Zurich
        x_4 = GeoPoint(47.3785431, 8.5484962)
        x_5 = GeoPoint(47.368649999999995, 8.539182)
        print utils.distance(x_1, x_2)
        print utils.distance(x_1, x_3)
        print utils.distance(x_4, x_5)
    
    def test_simple_search(self):
        x_1 = GeoPoint(7.1333, -73.0000) # Bucaramanga
        x_2 = GeoPoint(7.1233, -73.0000) # Some other point
        x_3 = GeoPoint(47.3667, 8.5500) # Zurich
        print utils.simple_search(x_1, [x_2, x_3], 2, 2000)
        print utils.simple_search(x_1, [x_2, x_3], 2, 10000000)
        print utils.simple_search(x_1, [x_2, x_3], 1, 10000000)

if __name__ == "__main__":
    unittest.main()
