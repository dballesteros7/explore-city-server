'''
Model for a mission waypoint which can be stored in Google's NDB.

Created on Dec 9, 2013

@author: diegob
'''
from google.appengine.ext import ndb

from geocell import utils
from models.general import GenericModel
from models.geopoint import GeoPoint


class MissionWaypoint(GenericModel):
    '''
    A waypoint is basically a tuple of two objects:

        1. A blob key indicating the associated picture.
        2. A geopoint model.
    '''

    ##############
    # Properties #
    ##############
    location = ndb.StructuredProperty(GeoPoint, required = True)
    reference_image = ndb.BlobKeyProperty(required = True)

    ##############
    # Queries    #
    ##############
    @classmethod
    def query_near(cls, central_point, max_distance, max_results):
        '''
        Query for mission waypoints, given a central point and a maximum
        distance returns close enough results up to a given limit.

        Distance is assumed in meters.
        '''
        if max_results is None:
            max_results = cls.MAX_QUERY_RESULTS
        max_res = central_point.resolution
        interest_points = []
        while(len(interest_points) < max_results and max_res >= 0):
            current_geocell = central_point.geocells[max_res]
            qry = cls.query(cls.location.geocells.IN([current_geocell]))
            results = qry.fetch(None)
            ordered_results = filter(lambda x : utils.distance(x.location, central_point) < max_distance, results)
            ordered_results = sorted(ordered_results, key = lambda x : utils.distance(x.location, central_point))
            interest_points = ordered_results
            max_res -= 1
        return interest_points[:max_results]

    @classmethod
    def query_box(cls, sw_corner, ne_corner, max_results):
        '''
        Query for mission waypoints, given a bounding box it returns
        all results inside up to the given limit.
        '''
        if max_results is None:
            max_results = cls.MAX_QUERY_RESULTS
        middle_point, radius = utils.calculate_box_center_and_distance(sw_corner, ne_corner)
        middle_point_model = GeoPoint.from_geocell_point(middle_point)
        max_res = middle_point_model.resolution
        interest_points = []
        while(len(interest_points) < max_results and max_res >= 0):
            current_geocell = middle_point_model.geocells[max_res]
            qry = cls.query(cls.location.geocells.IN([current_geocell]))
            results = qry.fetch(None)
            ordered_results = filter(lambda x : utils.distance(x.location, middle_point_model) < radius, results)
            ordered_results = sorted(ordered_results, key = lambda x : utils.distance(x.location, middle_point_model))
            interest_points = ordered_results
            max_res -= 1
        return interest_points[:max_results]