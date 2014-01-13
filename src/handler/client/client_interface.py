'''
Module that defines handlers for the different actions 
allowed for registered clients. Currently defines a handler
for retrieving mission waypoints and missions.

Created on Dec 16, 2013

@author: diegob
'''
from google.appengine.api.images import get_serving_url
import json
import webapp2

from models.geopoint import GeoPoint
from models.mission import Mission
from models.missionwaypoint import MissionWaypoint
from webutils import parseutils


class ClientWaypointProvider(webapp2.RequestHandler):
    '''
    Request handler that provides close waypoints given a central location
    and other query parameters.
    '''

    def post(self):
        """
        Process the request for waypoints.
        The input arguments for the post are:
        
        - latitude : Floating-point number that indicates the latitude of the query point.
        - longitude : Floating-point number that indicates the longitude of the query point.
        - max_distance : Distance in meters from the query point, defaults to 1km.
        - max_results : Maximum number of results to retrieve, defaults to 10.

        The syntax of the response is:
            {waypoints: [{latitude: <Longitude of the waypoint's location - Float>
                          longitude: <Latitude of the waypoint's location - Float>
                          image_url: <URL for the image associated to the waypoint - String>
                          name: <Name for the waypoint - String>},
                         ...,
                        ]
        """
        # Get all the relevant inputs, parse them properly
        qry_latitude = parseutils.parse_float(self.request.get('latitude'), -90, 90)
        qry_longitude = parseutils.parse_float(self.request.get('longitude'), -180, 180)
        qry_max_distance = parseutils.parse_float(self.request.get('max_distance',
                                                                   default_value = '1000'))
        qry_max_results = parseutils.parse_int(self.request.get('max_results',
                                                                default_value = '10'))

        # Generate a central point for query
        centralpoint = GeoPoint(latitude = qry_latitude,
                                longitude = qry_longitude)
        centralpoint.initialize_geocells()

        # Execute the query
        results = MissionWaypoint.query_near(centralpoint,
                                             qry_max_distance,
                                             qry_max_results)

        # Build the JSON response
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
    and other query parameters.
    '''

    def post(self):
        """
        Process the request for missions.
        The input arguments for the post are:
        
        - latitude : Floating-point number that indicates the latitude of the query point.
        - longitude : Floating-point number that indicates the longitude of the query point.
        - max_distance : Distance in meters from the query point, defaults to 1km.
        - max_results : Maximum number of results to retrieve, defaults to 10.

        The syntax of the response is:
            {missions: [ {name : <Name of the mission - String>,
                          waypoints: [ {latitude: <Longitude of the waypoint's location - Float>
                                        longitude: <Latitude of the waypoint's location - Float>
                                        image_url: <URL for the image associated to the waypoint - String>
                                        name: <Name for the waypoint - String>
                                        },
                                        ...,
                                     ]
                          },
                          ...,
                       ]
        """
        # Get all the relevant inputs, parse them properly
        qry_latitude = parseutils.parse_float(self.request.get('latitude'), -90, 90)
        qry_longitude = parseutils.parse_float(self.request.get('longitude'), -180, 180)
        qry_max_distance = parseutils.parse_float(self.request.get('max_distance',
                                                                   default_value = '1000'))
        qry_max_results = parseutils.parse_int(self.request.get('max_results',
                                                                default_value = '10'))

        # Generate a central point for query
        centralpoint = GeoPoint(latitude = qry_latitude,
                                longitude = qry_longitude)
        centralpoint.initialize_geocells()

        # Execute a query for close waypoints
        # It retrieves 10-times the number of results as the maximum of
        # missions requested to ensure all required missions are received.
        candidate_starts = MissionWaypoint.query_near(centralpoint,
                                                      qry_max_distance,
                                                      10 * qry_max_results)

        # Find the associated missions
        missionresults = Mission.query_by_waypoint(candidate_starts, qry_max_results)

        # Build the JSON response
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
