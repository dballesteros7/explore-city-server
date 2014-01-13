'''
Module that provides the handlers for administrator functions done
through the admin html interface. This is limited to waypoint creation and
retrieval.

It provides classes that serve the admin interface and provide the upload
handler for the reference images, as well as retrieving mission waypoints for
display.

Created on Dec 10, 2013

@author: diegob
'''

from google.appengine.api.images import get_serving_url
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import jinja2
import json
import os.path
import webapp2

from models.geopoint import GeoPoint
from models.missionwaypoint import MissionWaypoint


class AdminInterface(webapp2.RequestHandler):
    '''
    Handler that serves the admin interface where
    an administrator user can upload reference images and check
    the status of the waypoints in the system.
    '''
    def get(self):
        """
        Serve the admin interface
        """
        upload_url = blobstore.create_upload_url('/admin/upload_waypoint')
        template_values = {'destination_url' : upload_url}
        template = JINJA_ENVIRONMENT.get_template(os.path.join('html', 'admin', 'admin.html'))
        self.response.write(template.render(template_values))

class AdminWaypointUpload(blobstore_handlers.BlobstoreUploadHandler):
    '''
    Handler that accepts a new image uploaded using the admin interface
    and stores its model in the datastore
    '''
    def post(self):
        """
        Accept the incoming POST from the form
        """
        # TODO: Make the form post AJAX and process the blobstore
        # upload internally.
        # First retrieve the uploaded image key from the blobstore
        upload_files = self.get_uploads('upload_image')
        blob_info = upload_files[0]

        # TODO:
        # Filter the image to obtain the edge representation and store it
        # in the blobstore

        # Create a mission waypoint with the given image
        mission_waypoint = MissionWaypoint(reference_image = blob_info.key(),
                                           waypointname = self.request.get('image_name'),
                                           waypoint = GeoPoint(latitude = float(self.request.get('latitude')),
                                                               longitude = float(self.request.get('longitude'))))

        # Calculate the geocells for the waypoint before storing the mission
        mission_waypoint.waypoint.initialize_geocells()

        # Store in the datastore
        mission_waypoint.put()

        # Go back to the admin's lounge
        self.redirect('/admin')

class AdminWaypointRetrieval(webapp2.RequestHandler):
    '''
    Handler that process a request for a list of waypoints given a central
    point, max distance and max number of results.
    '''
    def post(self):
        """
        Process the request for waypoints
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

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.getcwd()),
    extensions = ['jinja2.ext.autoescape'],
    autoescape = True)
