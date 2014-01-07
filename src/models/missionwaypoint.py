'''
Model for a mission waypoint which can be stored in Google's NDB.

Created on Dec 9, 2013

@author: diegob
'''
from google.appengine.ext import ndb

from geocell import utils
from models.geopoint import GeoPoint


class MissionWaypoint(ndb.Model):
    '''
    A waypoint is basically a tuple of two objects:

        1. A blob key indicating the associated picture.
        2. A geopoint model.
    '''

    ##############
    # Properties #
    ##############
    waypoint = ndb.StructuredProperty(GeoPoint, required = True)
    reference_image = ndb.BlobKeyProperty(required = True)
    waypointname = ndb.StringProperty(required = True)

    ##############
    # Queries    #
    ##############
    @classmethod
    def query_near(cls, central_point, max_distance, max_results = 10):
        '''
        Query for mission waypoints, given a central point and a maximum
        distance returns close enough results up to a given limit.

        Distance must be in meters.
        '''
        max_res = central_point.resolution
        interest_points = []
        while(len(interest_points) < max_results and max_res >= 0):
            current_geocell = central_point.geocells[max_res]
            qry = cls.query(cls.waypoint.geocells.IN([current_geocell]))
            results = qry.fetch(None)
            ordered_results = filter(lambda x : utils.distance(x.waypoint, central_point) < max_distance, results)
            ordered_results = sorted(ordered_results, key = lambda x : utils.distance(x.waypoint, central_point))
            interest_points = ordered_results
            max_res -= 1
        return interest_points[:max_results]
