'''
Module that defines the class providing the HTTP verbs to interact
with user submissions in the server.
Created on Jan 13, 2014

@author: diegob
'''
from datetime import datetime
from google.appengine.api import users
from google.appengine.api.blobstore import BlobKey
import json

from handler.api.base_service import BaseResource
from models.mission import Mission
from models.missionwaypoint import MissionWaypoint
from models.submission import Submission
from models.user import User


class SubmissionResource(BaseResource):
    '''
    Webapp2 handler that provides CRUD functionality for user's submission
    objects in the system. This connects directly with Google's datastore
    to manipulate the mission objects.
    '''

    def post(self):
        '''
        Create a new submission for the requesting user, corresponding to
        a given mission and waypoint. The submission will be scored asynchronously
        and the score will be available later through the GET verb for the
        submission. If the submission score is low then it will be automatically
        deleted.
        
        The required parameters are:
            - mission: Mission name for the submisison
            - waypoint: Waypoint name for the submission
            - image_key: Valid key in the blobstore that corresponds to the image.
        
        The method only accepts JSON encoded bodies with content-type
        equal to 'application/json'.
        '''
        # Check the content type and parse the argument appropriately
        parameters = self.parse_request_body(urlencoded_accepted = False)

        # TODO: Ensure that submissions only come from authorized apps.
        if users.get_current_user() is None:
            # Anonymous uploads are just valid for testing.
            user_model = User.get_or_insert('Unique-Awesome-ID',
                                            email = "anonymous@explorecity.ch",
                                            nickname = "anonymous")
        else:
            current_user = users.get_current_user()
            user_model = User.get_or_insert(current_user.user_id(),
                                        nickname = current_user.nickname(),
                                        email = current_user.email())

        # Verify the input parameters
        model_params = self.validate_parameters_post(parameters)

        user_submission = Submission(parent = user_model.key,
                                     reference_mission = model_params['mission'].key,
                                     reference_waypoint = model_params['waypoint'].key,
                                     timestamp = datetime.utcnow(),
                                     submitted_image = model_params['image_key'])

        # TODO: Calculate asynchronous image score
        # Using the Tasks API

        submission_key = user_submission.put()

        # Return a response with the newly created object id.
        self.build_base_response(status_code = 202)
        response_results = {'name' : submission_key.id(),
                            'content_url' : self.uri_for('submissions-resource-named',
                                                         name = submission_key.id(),
                                                         _full = True)}
        self.response.out.write(json.dumps(response_results))

    def validate_parameters_post(self, parameters):
        '''
        Validate the POST arguments for creating a new submission. It checks
        existence and types and also casts the values if necessary.
        Returns a dictionary with the necessary parameters.
        '''
        model_params = {}
        required_parmaters = ['mission', 'waypoint', 'image_key']
        for param in required_parmaters:
            if param not in parameters:
                self.abort(400, detail = 'Missing required argument %s.' % param)
            if not parameters[param]:
                self.abort(400, detail = 'Bad value for param %s.' % param)

        reference_mission = Mission.get_by_id(parameters['mission'])
        if reference_mission is None:
            self.abort(400, detail = 'The given mission id does not exist.')
        reference_waypoint = MissionWaypoint.get_by_id(parameters['waypoint'])
        if reference_waypoint is None:
            self.abort(400, detail = 'The given waypoint id does not exist.')
        model_params['mission'] = reference_mission
        model_params['waypoint'] = reference_waypoint

        # TODO: Check for blob key existence
        model_params['image_key'] = BlobKey(parameters['image_key'])
        return model_params
