'''
Module that defines handlers for the different actions 
allowed for registered clients. Currently defines a handler
for retrieving mission waypoints and missions.

Created on Dec 16, 2013
Updated on Jan 07, 2013

@author: diegob
'''
from google.appengine.api.images import get_serving_url
import json
import webapp2

from models.geopoint import GeoPoint
from models.mission import Mission
from models.missionwaypoint import MissionWaypoint


class ClientWaypointProvider(webapp2.RequestHandler):
    '''
    Request handler that provides close waypoints given a central location
    and distance query parameters.
    '''

    def post(self):
        """
        Process the request for waypoints.
        """
        centralpoint = GeoPoint(latitude = float(self.request.get('latitude')),
                                longitude = float(self.request.get('longitude')))
        centralpoint.initialize_geocells()
        results = MissionWaypoint.query_near(centralpoint,
                                             float(self.request.get('max_distance')),
                                             int(self.request.get('max_results')))
        self.response.headers['Content-Type'] = 'application/json'
        response_results = {'waypoints' : []}
        for result in results:
            response_results['waypoints'].append({'latitude' : result.waypoint.latitude,
                                                  'longitude' : result.waypoint.longitude,
                                                  'image_url' : get_serving_url(result.reference_image),
                                                  'name' : result.waypointname})
        self.response.out.write(json.dumps(response_results))

class ClientMissionProvider(webapp2.RequestHandler):
    '''
    Request handler that provides close missions given a central starting location
    and distance query parameters.
    '''

    def post(self):
        """
        Process the request for missions.
        """
        centralpoint = GeoPoint(latitude = float(self.request.get('latitude')),
                                longitude = float(self.request.get('longitude')))
        centralpoint.initialize_geocells()
        candidate_starts = MissionWaypoint.query_near(centralpoint,
                                                      float(self.request.get('max_distance')),
                                                      int(self.request.get('max_results')))
        missionresults = Mission.query_by_waypoint(candidate_starts)
        self.response.headers['Content-Type'] = 'application/json'
        response_results = {'missions' : []}
        for result in missionresults:
            missionObject = {'name' : result.missionname,
                             'waypoints' : []}
            for waypoint in result.waypoints:
                waypoint.get()
                missionObject['waypoints'].append({'latitude' : waypoint.waypoint.latitude,
                                                   'longitude' : waypoint.waypoint.longitude,
                                                   'image_url' : get_serving_url(waypoint.reference_image),
                                                   'name' : waypoint.waypointname})
            response_results['missions'].append(missionObject)
        self.response.out.write(json.dumps(response_results))
