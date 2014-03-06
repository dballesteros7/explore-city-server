'''Module that provides the user API for the server.
'''
import json

from handler.api.base_service import BaseResource
from handler.auth import login_user
from lexicon import LexiconError
import lexicon
from models.user import TemporaryUser, User


class UserResource(BaseResource):
    '''Base API class for users, it handles the main CRUD functionality.
    '''

    def post(self):
        '''Callback that handles POST requests on the user resource, this
        allows the creation of users from an already created temporary user
        in the database.
        The required arguments expected in the body are:

        * user_key  -- Temporary user key in the datastore, it is expected as a 
                       value produced by urlsafe.
        * email -- E-mail for communicating with the user.
        * username -- Desired username.
        '''
        # Retrieve the parameters from the request
        parameters = self.parse_request_body()
        model_params = self.validate_parameters_post(parameters)

        # Retrieve the temporary user from the datastore
        # (assume existence for now)
        tempuser = TemporaryUser.query_by_urlsafe(model_params['user_key'])
        if tempuser is None:
            # Raise exception
            self.abort(400)

        # Create the user and store it
        newuser = User.create_user(model_params['email'],
                                   model_params['username'], tempuser)
        #TODO: Check for username uniqueness.
        newuser_key = newuser.put()

        # Destroy the temporal user record
        tempuser.delete()

        # Log in the user
        login_user(newuser, self.session)

        # Return the appropriate response
        self.build_base_response()
        response_results = {'username' : model_params['username'],
                            'content_url' :
                                        self.uri_for('users-resource-named',
                                                     userid = newuser_key.id(),
                                                     _full = True)}
        self.response.out.write(json.dumps(response_results))

    def validate_parameters_post(self, parameters):
        '''
        Validate the POST arguments for creating a new user. It checks the
        parameter against the lexicon, and then proceeds to some parsing.
        '''
        model_params = {}
        validator_map = {'username' : lexicon.username,
                         'email' : lexicon.email}
        required_parameters = ['username', 'email', 'user_key']
        for param in required_parameters:
            if param not in parameters:
                self.abort(400, 'Parameter: "%s" not provided.' % param)
            if param in validator_map:
                try:
                    validator_map[param](parameters[param])
                except LexiconError as ex:
                    self.abort(400, ex.msg)
            model_params[param] = parameters[param]
        return model_params