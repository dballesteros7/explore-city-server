'''
Model for a geopoint, it can be stored in Google's NDB.

The GeoPoint model is an abstraction of the same concept of geocell.geopoint.

Based on geomodel by Roman Nurik (https://code.google.com/p/geomodel/).

Created on Dec 6, 2013

@author: diegob
'''
from google.appengine.ext import ndb

from geocell.utils import computegeocell


class GeoPoint(ndb.Model):
    '''
    A GeoPoint object represents a location in the world, defined as a longitude
    and latitude, with additional information about the surrounding geocells.

    A geocell is a string with predefined length (also known as resolution). That
    encodes a bounding box for a point.

    The NDB model has a key defined as geocell:latitude(4 decimal digits):longitude(4 decimal digits).
    '''
    ##############
    # Properties #
    ##############

    latitude = ndb.FloatProperty(required = True)
    longitude = ndb.FloatProperty(required = True)
    resolution = ndb.IntegerProperty(required = False, default = 12)
    geocells = ndb.StringProperty(repeated = True)

    def initialize_geocells(self):
        '''
        Method for initializing the geocells for the GeoPoint.
        '''
        max_geocell = computegeocell(self)
        to_store = []
        for i in xrange(self.resolution):
            to_store.append(max_geocell[:i])
        to_store.append(max_geocell)
        geocells = to_store
        self.geocells = geocells
