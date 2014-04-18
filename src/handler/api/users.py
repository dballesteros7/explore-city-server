from google.appengine.api import urlfetch
import json
import urllib

from handler.api.base_service import BaseResource
from lexicon import LexiconError
import lexicon
from models.user import User
import secrets


class UserResource(BaseResource):
    """Base API class for users in the system."""

    def get(self, userkey = None):
        """Retrieves an user given any of the following parameters:
            email: e-mail for query.
            username: username for query.
            user_gid: Google Id for the user.
        If more than one of these parameters is provided, then they will be
        evaluated in the same order as listed above and only the first one
        to match will be returned.
        Also this get serves the named version where an urlsafe version of the
        key is expected.

        Args:
            userkey: URL-safe version of the key provided to retrieve a single user instance.
        """
        params = self.parse_request_body(json_accepted = False)
        user = None
        if userkey is not None:
            user = User.get_by_urlsafe(userkey)
        else:
            if 'email' in params:
                user = User.get_by_email(params['email'])
            if user is None and 'username' in params:
                user = User.get_by_username(params['username'])
            if user is None and 'user_gid' in params:
                user = User.get_by_google_id(params['user_gid'])

        response_results = {}
        if user is not None:
            self.build_base_response()
            response_results = {'username' : user.username,
                                'email' : user.email,
                                'content_url' :
                                        self.uri_for('users-resource-named',
                                                     userkey = user.key.urlsafe(),
                                                     _full = True)}
        else:
            self.build_base_response(404)
            response_results = {'details' :
                                    'No user matches the given information.'}
        self.response.out.write(json.dumps(response_results))

    def post(self):
        """Allows the creation of a new user from the mobile app.
        This requires the following parameters as
        part of the request body.

        * user_gid -- Identifier for the user in Google.
        * username -- Desired username for the user.
        * email -- Registered e-mail for the user.
        * authorization_code -- One-time authorization code for the server.

        If the username and email are valid and don't exist already in the
        system then a new user will be created
        and a session token will be issued to the calling app.
        """
        params = self.parse_request_body()
        processed_params = self.validate_parameters_post(params)

        # Exchange the given authorization code for
        authorization_fields = {'code' : processed_params['authorization_code'],
                                'client_id' : secrets.GOOGLE_APP_ID,
                                'client_secret' : secrets.GOOGLE_APP_SECRET,
                                'redirect_uri' : secrets.GOOGLE_REDIRECT_URI_ANDROID,
                                'grant_type' : 'authorization_code'}
        result = urlfetch.fetch(url = 'https://accounts.google.com/o/oauth2/token',
                                payload = urllib.urlencode(authorization_fields),
                                method = urlfetch.POST,
                                headers = {'Content-Type': 'application/x-www-form-urlencoded'})
        if result.status_code == 200:
            auth_credentials = json.loads(result.content)
            auth_credentials.update({'user_gid' : processed_params['user_gid']})
            newuser = User.create(processed_params['email'],
                                  processed_params['username'],
                                  auth_credentials)
            self.build_base_response()
            response_results = {'username' : newuser.username,
                                'content_url' :
                                        self.uri_for('users-resource-named',
                                                     userkey = newuser.key.urlsafe(),
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
                         'email' : lexicon.email}
        required_parameters = ['username', 'email',
                               'user_gid', 'authorization_code']
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
