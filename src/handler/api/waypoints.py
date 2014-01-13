'''
Module for the API class related to waypoint objects in the system.
Created on Jan 9, 2014

@author: diegob
'''
from google.appengine.api import namespace_manager
from google.appengine.api.images import get_serving_url
from google.appengine.ext.blobstore import BlobKey
import json
import webapp2

from models.geopoint import GeoPoint
from models.missionwaypoint import MissionWaypoint
from webutils import parseutils


class WaypointResource(webapp2.RequestHandler):
    '''
    Webapp2 handler that provides CRUD functionality for waypoint
    objects in the system. This connects directly with Google's datastore
    to manipulate the waypoint objects.
    '''

    def get(self, name = None):
        '''
        Provides the GET verb for the waypoints resource. It retrieves
        a list of waypoints according to the query parameters or all the
        waypoints in the system. If name is given then only the information
        about the given waypoint will be retrieved.

        The current supported parameters are:

        - longitude,latitude: Floating point numbers that indicate a query position. 
                              Only waypoints close to this point will be retrieved, given a maximum distance.
        - max_distance: Maximum distance (in meters) to limit the query for waypoints.
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
        qry_max_distance = parseutils.parse_float(self.request.get('max_distance',
                                                                   default_value = '1000'))

        if name is not None:
            results = MissionWaypoint.query_by_id(name)
        elif qry_latitude is not None and qry_longitude is not None:
            # Generate a central point for query
            centralpoint = GeoPoint(latitude = qry_latitude,
                                    longitude = qry_longitude)
            centralpoint.initialize_geocells()

            # Execute the query
            results = MissionWaypoint.query_near(centralpoint,
                                                 qry_max_distance,
                                                 qry_max_results)
        else:
            results = MissionWaypoint.query_all(qry_max_results)

        # Build the JSON response
        self.response.headers['Content-Type'] = 'application/json'
        response_results = {'waypoints' : []}
        for result in results:
            response_results['waypoints'].append({'latitude' : result.location.latitude,
                                                  'longitude' : result.location.longitude,
                                                  'image_url' : get_serving_url(result.reference_image),
                                                  'name' : result.key.id()})
        self.response.out.write(json.dumps(response_results))

    def post(self):
        '''
        Provides the POST verb for the waypoints resource. It creates a new
        mission waypoint in the datastore given its location information
        and the associated image blob key.
        
        It accepts parameters both in the body as JSON or as request arguments,
        the required arguments are:
            - latitude: Floating point latitude of the waypoint
            - longitude: Floating point longitude of the waypoint
            - image_key: Valid key in the blobstore for the reference image
            - name: Name for the waypoint, must be non-existent
        
        The accepted content types are 'application/json' and 
        'application/x-www-form-urlencoded'
        '''
        # TODO: Access control
        # Check the content type and parse the argument appropriately
        if self.request.headers.get('Content_Type') == 'application/json':
            # TODO: Catch bad JSON
            parameters = json.loads(self.request.body)
        elif self.request.headers.get('Content_Type') == 'application/x-www-form-urlencoded':
            parameters = self.request.params
        else:
            webapp2.abort(400, detail = 'Bad content type.')
        model_params = self.validate_parameters_post(parameters)

        # Create the waypoint model object and store in the datastore
        location = GeoPoint(latitude = model_params['latitude'],
                            longitude = model_params['longitude'])
        location.initialize_geocells()

        waypoint = MissionWaypoint(id = model_params['name'],
                                   location = location,
                                   reference_image = BlobKey(model_params['image_key']))
        waypoint_key = waypoint.put()

        # Return a response with the newly created object id.
        self.response.headers['Content-Type'] = 'application/json'
        response_results = {'name' : waypoint_key.id(),
                            'content_url' :
                                        self.uri_for('waypoints-resource-named',
                                                     name = waypoint_key.id(),
                                                     _full = True)}
        self.response.out.write(json.dumps(response_results))

    def validate_parameters_post(self, parameters):
        '''
        Validate the POST arguments for creating a new waypoint. It checks
        existence and types and also casts the values if necessary.
        Returns a dictionary with the necessary parameters.
        '''
        # TODO: Implement checks
        model_params = {}
        model_params['latitude'] = float(parameters['latitude'])
        model_params['longitude'] = float(parameters['longitude'])
        model_params['name'] = parameters['name']
        model_params['image_key'] = parameters['image_key']
        if MissionWaypoint.get_by_id(model_params['name']) is not None:
            self.abort(400, 'Mission waypoint with this id already exists.')
        return model_params
