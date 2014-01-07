'''
Test module for the geopoint and utils modules.
Created on Dec 6, 2013

@author: diegob
'''
import unittest

from geocell import utils
from models.geopoint import GeoPoint

class GeoPointTest(unittest.TestCase):
    '''
    Check the basic functionality of the GeoPoint class, this also
    checks the sanity of the utils functions relating to GeoPoint objects.
    '''

    def test_creation(self):
        x = GeoPoint(latitude = 7.1333, longitude = -73.0000)
        print x.geocells

    def test_distance(self):
        x_1 = GeoPoint(latitude = 7.1333, longitude = -73.0000) # Bucaramanga
        x_2 = GeoPoint(latitude = 7.1233, longitude = -73.0000) # Some other point
        x_3 = GeoPoint(latitude = 47.3667, longitude = 8.5500) # Zurich
        print utils.distance(x_1, x_2)
        print utils.distance(x_1, x_3)

if __name__ == "__main__":
    unittest.main()