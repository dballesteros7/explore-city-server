'''
Module for the API class related to mission objects in the system.
Created on Jan 10, 2014

@author: diegob
'''
from google.appengine.api.images import get_serving_url
from google.appengine.ext.ndb.key import Key
import json
import webapp2

from models.geopoint import GeoPoint
from models.mission import Mission
from models.missionwaypoint import MissionWaypoint
from webutils import parseutils


class MissionResource(webapp2.RequestHandler):
    '''
    Webapp2 handler that provides CRUD functionality for mission
    objects in the system. This connects directly with Google's datastore
    to manipulate the mission objects.
    '''

    def get(self, name = None):
        '''
        Provides the GET verb for the missions resource. It retrieves
        a list of missions according to the query parameters or all the
        missions in the system. If name is given then only the information
        about the given mission will be retrieved.

        The current supported parameters are:

        - longitude,latitude: Floating point numbers that indicate a query position. 
                              Only missions starting close to this point will be retrieved, given a maximum distance.
        - max_distance: Maximum distance (in meters) to limit the query for mission starting points.
        - max_results: Maximum number of results to return.
        '''
        # Check the kind of query to be made.
        # Get all the relevant inputs, parse them properly
        qry_latitude = None
        qry_longitude = None
        qry_max_results = None
        if 'latitude' in self.request.arguments() and 'longitude' in self.request.arguments():
            qry_latitude = parseutils.parse_float(self.request.get('latitude'), -90, 90)
            qry_longitude = parseutils.parse_float(self.request.get('longitude'), -180, 180)
        if 'max_results' in self.request.arguments():
            qry_max_results = parseutils.parse_int(self.request.get('max_results',
                                                                    default_value = '10'),
                                                   1)
        qry_max_distance = parseutils.parse_int(self.request.get('max_distance',
                                                                 default_value = '1000'))

        if name is not None:
            results = Mission.query_by_id(name)
        elif qry_latitude is not None and qry_longitude is not None:
            # Generate a central point for query
            centralpoint = GeoPoint(latitude = qry_latitude,
                                    longitude = qry_longitude)
            centralpoint.initialize_geocells()

            # Get all close waypoints
            startingpoints = MissionWaypoint.query_near(centralpoint,
                                                        qry_max_distance,
                                                        None)
            results = []
            if startingpoints:
                startingpoints_keys = [x.key for x in startingpoints]
                # Find all missions starting in any of the given waypoints
                results = Mission.query_by_waypoint(startingpoints_keys, qry_max_results)
        else:
            results = Mission.query_all(qry_max_results)

        # Build the JSON response
        self.response.headers['Content-Type'] = 'application/json'
        response_results = {'missions' : []}
        for mission in results:
            missionObject = {'name' : mission.key.id(),
                             'waypoints' : []}
            for waypointKey in mission.waypoints:
                waypoint = waypointKey.get()
                missionObject['waypoints'].append({'latitude' : waypoint.location.latitude,
                                                   'longitude' : waypoint.location.longitude,
                                                   'image_url' : get_serving_url(waypoint.reference_image),
                                                   'name' : waypointKey.id()})
            response_results['missions'].append(missionObject)
        self.response.out.write(json.dumps(response_results))

    def post(self):
        '''
        Provides the POST verb for the waypoints resource. It creates a new
        mission waypoint in the datastore given its location information
        and the associated image blob key.

        It accepts parameters only in the body as JSON,
        the required arguments are:
            - name : Unique name for the mission
            - waypoints: A list of JSON strings with the unique names of the waypoints
                        for the mission, the waypoints will be stored in the given
                        order.

        The only accepted content type is 'application/json'.
        '''
        # TODO: Access control
        # Check the content type and parse the argument appropriately
        if self.request.headers.get('Content_Type') == 'application/json':
            # TODO: Catch bad JSON
            parameters = json.loads(self.request.body)
        else:
            self.abort(400, detail = 'Bad content type.')
        model_parameters = self.validate_parameters_post(parameters)
        mission = Mission(id = model_parameters['name'],
                          startWaypoint = model_parameters['waypoints'][0],
                          waypoints = model_parameters['waypoints'])
        mission_key = mission.put()

        # Return a response with the newly created object id.
        self.response.headers['Content-Type'] = 'application/json'
        response_results = {'name' : mission_key.id(),
                            'content_url' : self.uri_for('missions-resource-named',
                                                         name = mission_key.id(),
                                                         _full = True)}
        self.response.out.write(json.dumps(response_results))

    def validate_parameters_post(self, parameters):
        '''
        Validate the POST arguments for creating a new mission. It checks
        existence and types and also casts the values if necessary.
        Returns a dictionary with the necessary parameters.
        '''
        model_parameters = {}
        required_parmaters = ['name', 'waypoints']
        for param in required_parmaters:
            if param not in parameters:
                self.abort(400, detail = 'Missing required argument %s.' % param)
            if not parameters[param]:
                self.abort(400, detail = 'Bad value for param %s.' % param)

        model_parameters['name'] = parameters['name']
        if Mission.get_by_id(model_parameters['name']) is not None:
            self.abort(400, detail = 'The given mission id already exists.')
        model_parameters['waypoints'] = []
        for waypoint_id in parameters['waypoints']:
            candidate_key = Key(MissionWaypoint, waypoint_id)
            if candidate_key.get() is None:
                self.abort(400, detail = 'The given waypoint: %s does not exist in the datastore.' % waypoint_id)
            model_parameters['waypoints'].append(candidate_key)

        return model_parameters
