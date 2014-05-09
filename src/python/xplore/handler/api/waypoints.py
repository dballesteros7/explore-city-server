from google.appengine.api.images import get_serving_url
from google.appengine.ext import ndb
from google.appengine.ext.blobstore import BlobInfo
from google.appengine.ext.ndb.blobstore import BlobKey
import json

from geotypes import Point
from xplore.database.models import MissionWaypoint
from xplore.database.utils import get_missions_for_waypoint
from xplore.handler.api.base_service import BaseResource, QueryType
from xplore.webutils import parseutils


class WaypointResource(BaseResource):
    """
    Webapp2 handler that provides CRUD functionality for waypoint
    objects in the system. This connects directly with Google's datastore
    to manipulate the waypoint objects.
    """

    def get(self, name=None):
        """
        Provides the GET verb for the waypoints resource. It retrieves
        a list of waypoints according to the query parameters or all the
        waypoints in the system. If name is given then only the information
        about the given waypoint will be retrieved.

        The current supported parameters are:

        - longitude,latitude: Floating point numbers that indicate a
          query position. Only waypoints close to this point will be retrieved,
          given a maximum distance.
        - max_distance: Maximum distance (in meters) to limit
          the query for waypoints.
        - max_results: Maximum number of results to return.
        - swlongitude, swlatitude: Floating point numbers that indicate a
          bounding box query. This is the southwest corner of the box.
        - nelongitude, nelatitude: Floating point numbers that indicate a
          bounding box query. This is the northeast corner of the box.
        """
        qry_params = self.validate_parameters_get(self.request.params)
        if name is not None:
            results = MissionWaypoint.get_by_property('name', name)
        elif qry_params['type'] == QueryType.DISTANCE_FROM_CENTER:
            # Generate a central point for query
            center = Point(qry_params['lat'], qry_params['lng'])
            # Execute the query
            results = MissionWaypoint.query_near(center,
                                                 qry_params['max_results'],
                                                 qry_params['distance'])
        elif qry_params['type'] == QueryType.UNBOUNDED:
            results = MissionWaypoint.get_all(qry_params['max_results'])
        elif qry_params['type'] == QueryType.BOUNDING_BOX:
            results = MissionWaypoint.query_box(qry_params['nelat'],
                                                qry_params['nelong'],
                                                qry_params['swlat'],
                                                qry_params['swlong'],
                                                qry_params['max_results'])
        else:
            self.abort(400, detail='Query not recognized for this resource.')

        # Build the JSON response
        self.build_base_response()
        response_results = {'waypoints' : []}
        for result in results:
            options = {'size' : 0}
            if 'image_size' in qry_params:
                options['size'] = qry_params['image_size']
            response_results['waypoints'].append({'latitude' :
                                                    result.location.lat,
                                                  'longitude' :
                                                    result.location.lon,
                                                  'image_url' :
                                                    get_serving_url(
                                                        result.image,
                                                        **options),
                                                  'image_key' :
                                                    str(result.image),
                                                  'name' :
                                                    result.name})
        self.response.out.write(json.dumps(response_results))

    def post(self):
        """
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
        """
        # Check the content type and parse the argument appropriately
        parameters = self.parse_request_body()
        model_params = self.validate_parameters_post(parameters)

        # Create the waypoint model object and store in the datastore
        location = ndb.GeoPt(model_params['latitude'],
                             model_params['longitude'])

        waypoint = MissionWaypoint.create_with_default_ancestor(
                                    name=model_params['name'],
                                    location=location,
                                    image=BlobKey(model_params['image_key']))
        waypoint.put()

        # Return a response with the newly created object id.
        self.build_base_response(status_code=201)
        response_results = {'name' : waypoint.name,
                            'content_url' :
                                        self.uri_for('waypoints-resource-named',
                                                     name=waypoint.name,
                                                     _full=True)}
        self.response.out.write(json.dumps(response_results))

    def put(self, name):
        """
        Provides the PUT verb for the waypoint resource. It allows the update
        of an existing waypoint given its name and updated information.
        The accepted parameters are:
        
        - latitude, longitude: Floating point coordinates for the new
          location of the waypoint.
        - image_key: String corresponding to an updated image key on
          the BlobStore.

        Any combination of the 3 parameters can be given and just the ones
        provided will be changed in the stored object.

        The accepted content types are 'application/json' and 
        'application/x-www-form-urlencoded'
        """
        # Check the content type and parse the arguments appropriately
        # Validate them as well
        parameters = self.parse_request_body()
        model_params = self.validate_parameters_put(name, parameters)

        # Update the waypoint object and store it back in the datastore
        waypoint_to_update = model_params['waypoint']
        if 'latitude' in model_params \
            or 'longitude' in model_params:
            new_location = ndb.GeoPt(model_params.get(
                                        'latitude',
                                         waypoint_to_update.location.lat),
                                     model_params.get(
                                        'longitude',
                                        waypoint_to_update.location.lon))
            waypoint_to_update.location = new_location

        if 'image_key' in model_params:
            image_key = BlobKey(parameters['image_key'])
            if image_key != waypoint_to_update.image:
                BlobInfo.get(waypoint_to_update.image).delete()
                waypoint_to_update.image = image_key

        waypoint_to_update.put()

        # Return a response with the newly created object id.
        self.build_base_response()
        response_results = {'name' : waypoint_to_update.name,
                            'content_url' :
                                    self.uri_for('waypoints-resource-named',
                                                 name=waypoint_to_update.name,
                                                 _full=True)}
        self.response.out.write(json.dumps(response_results))

    def delete(self, name):
        """
        Provides the DELETE verb for the waypoint resource. It allows the
        deletion of waypoint given its ID. It deletes the resource if it exists
        and throws an exception otherwise. It also deletes from the Blobstore
        the reference image associated with it.
        """
        # Retrieve the waypoint to delete and check that it exists.
        results = MissionWaypoint.get_by_property('name', name)
        if not results:
            self.abort(400, detail='Specified resource does not exist.')

        # Delete the waypoint
        waypoint_to_delete = results[0]
        waypoint_to_delete.delete()

        # TODO: Clean all submissions related to this waypoint
        self.build_base_response()
        self.response.out.write(json.dumps(None))

    def missions_for_waypoint(self, name):
        waypoint = MissionWaypoint.get_by_property('name', name)[0]
        results = get_missions_for_waypoint(waypoint.key)
        parsed_results = [m.to_json() for m in results]
        self.build_base_response()
        self.response.out.write(json.dumps(parsed_results))

    ###########################################################################
    # Utility methods
    ###########################################################################

    def validate_parameters_get(self, parameters):
        '''
        Validate the GET arguments for retrieving waypoints. It checks existence
        and types, it also casts the values if necessary. It returns a
        dictionary with the necessary parameters.
        The input parameters must be a dictionary from the request WebOp object.
        '''
        qry_params = {}
        if 'max_results' in parameters:
            qry_params['max_results'] = parseutils.parse_int(parameters['max_results'],
                                                             1)
        else:
            qry_params['max_results'] = None
        if 'image_size' in parameters:
            qry_params['image_size'] = parseutils.parse_int(parameters['image_size'], 100)
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
                self.abort(400, detail='Bounding box parameters are incomplete.')
            qry_params['swlat'] = parseutils.parse_float(parameters['swlatitude'], -90, 90)
            qry_params['swlong'] = parseutils.parse_float(parameters['swlongitude'], -180, 180)
            qry_params['nelat'] = parseutils.parse_float(parameters['nelatitude'], -90, 90)
            qry_params['nelong'] = parseutils.parse_float(parameters['nelongitude'], -180, 180)
            qry_params['type'] = QueryType.BOUNDING_BOX
        return qry_params

    def validate_parameters_post(self, parameters):
        '''
        Validate the POST arguments for creating a new waypoint. It checks
        existence and types and also casts the values if necessary.
        Returns a dictionary with the necessary parameters.
        '''
        model_params = {}
        model_params['latitude'] = parseutils.parse_float(
                                                parameters['latitude'], -90, 90)
        model_params['longitude'] = parseutils.parse_float(
                                            parameters['longitude'], -180, 180)
        model_params['name'] = parameters['name']
        model_params['image_key'] = parameters['image_key']

        if MissionWaypoint.get_by_property('name', model_params['name']):
            self.abort(400, detail='Specified resource already exists.')

        return model_params

    def validate_parameters_put(self, name, parameters):
        '''
        Validate the PUT arguments for updating an existing waypoint. It checks
        that the waypoint already exists and casts the update values if
        necessary. It returns a dictionary with the necessary parameters.
        '''
        model_params = {}
        model_params['waypoint'] = MissionWaypoint.get_by_property('name',
                                                                   name)[0]
        if model_params['waypoint'] is None:
            self.abort(400, detail='Specified resource does not exist.')
        if 'latitude' in parameters:
            model_params['latitude'] = parseutils.parse_float(
                                                parameters['latitude'], -90, 90)
        if 'longitude' in parameters:
            model_params['longitude'] = parseutils.parse_float(
                                            parameters['longitude'], -180, 180)
        if 'image_key' in parameters:
            model_params['image_key'] = parameters['image_key']
        return model_params

