'''
Module for the API class related to mission objects in the system.
Created on Jan 10, 2014

@author: diegob
'''
from google.appengine.api.images import get_serving_url
import json

from geocell.geopoint import GeoPoint as SimpleGeoPoint
from handler.api.base_service import BaseResource, QueryType
from models.geopoint import GeoPoint
from models.mission import Mission
from models.missionwaypoint import MissionWaypoint
from webutils import parseutils
from handler.auth import login_required


class MissionResource(BaseResource):
    '''
    Webapp2 handler that provides CRUD functionality for mission
    objects in the system. This connects directly with Google's datastore
    to manipulate the mission objects.
    '''

    ###########################################################################
    # HTTP Verbs
    ###########################################################################

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
        qry_params = self.validate_parameters_get(self.request.params)

        if name is not None:
            results = Mission.query_by_id(name)
        elif qry_params['type'] == QueryType.DISTANCE_FROM_CENTER:
            # Generate a central point for query
            centralpoint = GeoPoint(latitude = qry_params['lat'],
                                    longitude = qry_params['lng'])
            centralpoint.initialize_geocells()

            # Get all close waypoints
            startingpoints = MissionWaypoint.query_near(centralpoint,
                                                        qry_params['distance'],
                                                        None)
            results = []
            if startingpoints:
                startingpoints_keys = [x.key for x in startingpoints]
                # Find all missions starting in any of the given waypoints
                results = Mission.query_by_waypoint(startingpoints_keys, qry_params['max_results'])
        elif qry_params['type'] == QueryType.BOUNDING_BOX:
            # Get all waypoints in the bounding box
            southwest_corner = SimpleGeoPoint(latitude = qry_params['swlat'],
                                              longitude = qry_params['swlong'])
            northeast_corner = SimpleGeoPoint(latitude = qry_params['nelat'],
                                              longitude = qry_params['nelong'])
            startingpoints = MissionWaypoint.query_box(southwest_corner,
                                                northeast_corner,
                                                qry_params['max_results'])
            results = []
            if startingpoints:
                startingpoints_keys = [x.key for x in startingpoints]
                # Find all missions starting in any of the given waypoints
                results = Mission.query_by_waypoint(startingpoints_keys, qry_params['max_results'])
        else:
            results = Mission.query_all(qry_params['max_results'])

        # Build the JSON response
        self.build_base_response()
        response_results = {'missions' : []}
        for mission in results:
            missionObject = {'name' : mission.key.id(),
                             'waypoints' : []}
            if qry_params['detailed']:
                for waypointKey in mission.waypoints:
                    waypoint = waypointKey.get()
                    missionObject['waypoints'].append({'latitude' : waypoint.location.latitude,
                                                       'longitude' : waypoint.location.longitude,
                                                       'image_url' : get_serving_url(waypoint.reference_image),
                                                       'name' : waypointKey.id()})
            response_results['missions'].append(missionObject)
        self.response.out.write(json.dumps(response_results))

    @login_required(redirect = False, admin_only = True)
    def post(self):
        '''
        Provides the POST verb for the missions resource. It creates a new
        mission in the datastore given an orderered list of waypoints.

        It accepts parameters only in the body as JSON,
        the required arguments are:
            - name : Unique name for the mission
            - waypoints: A list of JSON strings with the unique names of the waypoints
                        for the mission, the waypoints will be stored in the given
                        order.

        The only accepted content type is 'application/json'.
        '''
        # Check the content type and parse the argument appropriately
        parameters = self.parse_request_body(urlencoded_accepted = False)
        model_params = self.validate_parameters_post(parameters)

        # Build the mission object and store it in the datastore
        mission = Mission.build(id = model_params['name'],
                                start_waypoint = model_params['waypoints'][0],
                                waypoints = model_params['waypoints'])

        mission_key = mission.put()

        # Return a response with the newly created object id.
        self.build_base_response(status_code = 201)
        response_results = {'name' : mission_key.id(),
                            'content_url' : self.uri_for('missions-resource-named',
                                                         name = mission_key.id(),
                                                         _full = True)}
        self.response.out.write(json.dumps(response_results))

    @login_required(redirect = False, admin_only = True)
    def put(self, name):
        '''
        Provides the PUT verb for the waypoints resource. It allows editing
        the list of waypoints in a mission. The list of waypoints is replaced
        by the ordered list of waypoints given in the PUT request body.

        The accepted arguments are:
            - waypoints: Ordered list of waypoints that will replace the
                         waypoints in the mission.

        The only format allowed is JSON and the content type should be
        'application/json'.
        '''
        # Check the content type and parse the argument appropriately
        parameters = self.parse_request_body(urlencoded_accepted = False)
        parameters['name'] = name
        model_params = self.validate_parameters_put(parameters)

        # Build the mission object and store it in the datastore
        mission_to_update = model_params['mission']
        mission_to_update.start_waypoint = model_params['waypoints'][0]
        mission_to_update.waypoints = model_params['waypoints']
        mission_to_update.put()

        # Return a response with the newly created object id.
        self.build_base_response()
        response_results = {'name' : mission_to_update.key.id(),
                            'content_url' : self.uri_for('missions-resource-named',
                                                         name = mission_to_update.key.id(),
                                                         _full = True)}
        self.response.out.write(json.dumps(response_results))

    @login_required(redirect = False, admin_only = True)
    def delete(self, name):
        '''
        Provides the DELETE verb for the missions resource. It allows deleting
        a mission given its name. This DOES NOT delete the associated waypoints.
        '''
        # Retrieve the mission to delete and check that it exists.
        mission_to_delete = Mission.query_by_id(name)
        if not mission_to_delete:
            self.abort(400, detail = 'Specified resource does not exist.')

        # Delete the mission
        mission_to_delete = mission_to_delete[0]
        mission_to_delete.delete()

        # TODO: Clean all submissions related to this mission
        self.build_base_response()
        self.response.out.write(json.dumps(None))

    ###########################################################################
    # Utility methods
    ###########################################################################

    def validate_parameters_get(self, parameters):
        '''
        Validate the GET arguments for retrieving missions. It checks existence
        and types, it also casts the values if necessary. It returns a
        dictionary with the necessary parameters.
        The input parameters must be a dictionary from the request WebOp object.
        '''
        qry_params = {}
        if 'max_results' in parameters:
            qry_params['max_results'] = parseutils.parse_int(parameters.get('max_results', '10'),
                                                             1)
        else:
            qry_params['max_results'] = None
        is_bounding_qry = parseutils.parse_bool(parameters.get('bounding_box', 'false'))
        if not is_bounding_qry:
            if 'latitude' in parameters and 'longitude' in parameters:
                qry_params['lat'] = parseutils.parse_float(parameters['latitude'], -90, 90)
                qry_params['lng'] = parseutils.parse_float(parameters['longitude'], -180, 180)
                qry_params['distance'] = parseutils.parse_float(parameters.get('max_distance', '1000'))
                qry_params['type'] = QueryType.DISTANCE_FROM_CENTER
            else:
                qry_params['type'] = QueryType.UNBOUNDED
        else:
            if 'swlatitude' not in parameters or 'swlongitude' not in parameters \
                or 'nelatitude' not in parameters or 'nelongitude' not in parameters:
                self.abort(400, detail = 'Bounding box parameters are incomplete.')
            qry_params['swlat'] = parseutils.parse_float(parameters['swlatitude'], -90, 90)
            qry_params['swlong'] = parseutils.parse_float(parameters['swlongitude'], -180, 180)
            qry_params['nelat'] = parseutils.parse_float(parameters['nelatitude'], -90, 90)
            qry_params['nelong'] = parseutils.parse_float(parameters['nelongitude'], -180, 180)
            qry_params['type'] = QueryType.BOUNDING_BOX
        qry_params['detailed'] = parseutils.parse_bool(parameters.get('detailed', 'True'));
        return qry_params

    def validate_parameters_post(self, parameters, check_existence = True):
        '''
        Validate the POST arguments for creating a new mission. It checks
        existence and types and also casts the values if necessary.
        Returns a dictionary with the necessary parameters.
        '''
        model_params = {}
        required_parameters = ['name', 'waypoints']
        for param in required_parameters:
            if param not in parameters:
                self.abort(400, detail = 'Missing required argument %s.' % param)
            if not parameters[param]:
                self.abort(400, detail = 'Bad value for param %s.' % param)

        # TODO: Check the name against the Lexicon
        model_params['name'] = parameters['name']
        stored_mission = Mission.query_by_id(model_params['name'])
        if check_existence and stored_mission:
            self.abort(400, detail = 'Specified resource already exists.')
        elif not check_existence and not stored_mission:
            self.abort(400, detail = 'Specified resource does not exist.')
        elif not check_existence:
            model_params['mission'] = stored_mission[0]

        model_params['waypoints'] = []
        for waypoint_id in parameters['waypoints']:
            # TODO: Check waypoint id against the Lexicon
            candidate_waypoint = MissionWaypoint.query_by_id(waypoint_id)
            if not candidate_waypoint:
                self.abort(400, detail = 'Specified resource does not exist.')
            model_params['waypoints'].append(candidate_waypoint[0].key)

        return model_params

    def validate_parameters_put(self, parameters):
        '''
        Validate the PUT arguments for updating a mission. It checks
        existence and types and also casts the values if necessary.
        Returns a dictionary with the necessary parameters.

        It is just an alias for validate_parmaeters_post(check_existence = False)
        '''
        return self.validate_parameters_post(parameters, check_existence = False)
