'''
Module that defines the GeoPoint class.

Based on geomodel by Roman Nurik (https://code.google.com/p/geomodel/).
Created on Dec 5, 2013

@author: diegob
'''

import hashlib

from geocell.utils import computegeocell

class GeoPoint():
    '''
    A GeoPoint object represents a location in the world, defined as a longitude
    and latitude, with additional information about the surrounding geocells.

    A geocell is a string with predefined length (also known as resolution). That
    encodes a bounding box for a point.
    '''

    def __init__(self, latitude, longitude, resolution = 12):
        '''
        Constructs a geopoint with the given latitude and longitude, plus
        it computes the geocells with resolutions from 1 to the resolution
        value given.
        The default resolution value of 12 results in bounding boxes of
        around 0.84m side-length (i.e. a diagonal distance of 1.19m) which
        should be enough precision for many applications.
        '''
        self.latitude = latitude
        self.longitude = longitude
        self.resolution = resolution
        self.max_geocell = computegeocell(self)


    def __repr__(self):
        return '<%s>' % self.__str__()

    def __str__(self):
        return '%s: %.4f,%.4f' % (self.max_geocell, self.latitude, self.longitude)

    ######################################
    # Methods for hashing and comparison #
    ######################################

    def __hash__(self):
        m = hashlib.md5()
        m.update(self.max_geocell)
        m.update(str(self.latitude))
        m.update(str(self.longitude))
        return int(m.hexdigest(), base = 16)

    def __eq__(self, other):
        if(self.latitude == other.latitude):
            return self.longitude == other.longitude
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return NotImplemented

    def __ge__(self, other):
        return NotImplemented
