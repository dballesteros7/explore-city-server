'''Module that provides the user API for the server.
'''
from google.appengine.api import urlfetch
import json
import urllib

from handler.api.base_service import BaseResource
from handler.auth import login_user
from lexicon import LexiconError
import lexicon
from models.user import TemporaryUser, User
import secrets


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
        # TODO: Check for username uniqueness.
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

class MobileUserResource(BaseResource):
    '''Base API class for users that start their experience in the mobile app.
    '''

    def get(self):
        '''Provides the functionality to retrieve an user given its id in
        some service. Currently only supports Google as a provider.
        '''
        params = self.parse_request_body(json_accepted = False)
        user = User.check_user_existence_for_mobile(user_id = params['id'],
                                                    provider = params['provider'])
        self.build_base_response()
        response_results = {}
        if user is not None:
            response_results = {'username' : user.username,
                                'content_url' :
                                        self.uri_for('users-resource-named',
                                                     userid = user.key.urlsafe(),
                                                     _full = True)}
        self.response.out.write(json.dumps(response_results))

    def post(self):
        '''Allows the creation of a new user from the mobile app.
        This requires the following parameters as
        part of the request body.

        * provider -- Identifier of the authentication service used, e.g. google.
        * user_id -- Identifier for the user in the authentication service.
        * username -- Desired username for the user.
        * email -- Registered e-mail for the user.
        * authorization_code -- One-time authorization code for the server.
        * Any other authentication parameters required by the IdentityProvider
          class.

        If the username and email are valid and don't exist already in the
        system then a new user will be created
        and a session token will be issued to the calling app.
        '''
        params = self.parse_request_body()
        processed_params = self.validate_parameters_post(params)

        # Currently it only supports google authentication an requires the
        # following procedure to obtain a long lived server access token and
        # refresh token from the given access token from the mobile app.
        authorization_fields = {"code" : processed_params["authorization_code"],
                                "client_id" : secrets.GOOGLE_APP_ID,
                                "client_secret" : secrets.GOOGLE_APP_SECRET,
                                "redirect_uri" : "urn:ietf:wg:oauth:2.0:oob",
                                "grant_type" : "authorization_code"}
        result = urlfetch.fetch(url = "https://accounts.google.com/o/oauth2/token",
                                payload = urllib.urlencode(authorization_fields),
                                method = urlfetch.POST,
                                headers = {'Content-Type': 'application/x-www-form-urlencoded'})
        if result.status_code == 200:
            auth_credentials = json.loads(result.content)
            auth_credentials.update({'user_id' : processed_params['user_id'],
                                     'provider' : processed_params['provider']})
            newuser = User.create_user_from_mobile(processed_params["email"],
                                                   processed_params["username"],
                                                   put = True,
                                                   **auth_credentials)
            self.build_base_response()
            response_results = {'username' : newuser.username,
                                'content_url' :
                                        self.uri_for('users-resource-named',
                                                     userid = newuser.key.id(),
                                                     _full = True)}
            self.response.out.write(json.dumps(response_results))
        else:
            print result.content
            self.abort(result.status_code)

    def validate_parameters_post(self, parameters):
        '''Validate the POST arguments for creating a new user using the
        Lexicon.
        The parameters for the POST are as described in the post method
        docstring.
        Returns:
            A dictionary with the required arguments for the post method
            with values parsed to match the appriopriate types.
        '''
        model_params = {}
        validator_map = {'username' : lexicon.username,
                         'email' : lexicon.email,
                         'provider' : lexicon.provider}
        required_parameters = ['username', 'email', 'provider',
                               'user_id', 'authorization_code']
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
