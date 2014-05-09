from google.appengine.api import urlfetch, users
import json
import urllib

from xplore import lexicon
from xplore import secrets
from xplore.database.models import User, GoogleIdentity
from xplore.handler.api.base_service import BaseResource
from xplore.lexicon import LexiconError


class UserResource(BaseResource):
    """Base API class for users in the system."""

    def get(self, userkey=None):
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
        params = self.parse_request_body(json_accepted=False)
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
                                                     userkey=user.key.urlsafe(),
                                                     _full=True)}
        else:
            self.build_base_response(404)
            response_results = {'details' :
                                    'No user matches the given information.'}
        self.response.out.write(json.dumps(response_results))

    def me(self, redirect_url=None):
        """Retrieves the information about the user currently logged in, using
        the users service from the GAE.
        """
        gae_user = users.get_current_user();
        result_user = {}
        if gae_user:
            user_gid = gae_user.user_id()
            local_user = User.get_by_google_id(user_gid)
            if local_user:
                result_user['username'] = local_user.username
                result_user['status'] = 0
                result_user['rank'] = 'Xplorer'
                result_user['logout_url'] = users.create_logout_url('/home')
            else:
                result_user['logout_url'] = users.create_logout_url('/home')
                result_user['status'] = 1
        else:
            result_user['status'] = 2
            result_user['login_url'] = users.create_login_url(redirect_url or '/home')
        self.build_base_response()
        self.response.out.write(json.dumps(result_user))

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
        if 'web' in params:
            if users.get_current_user():
                gae_user = users.get_current_user()
                google_id = GoogleIdentity.create_with_default_ancestor(
                                                  user_gid = gae_user.user_id())
                User.create_with_default_ancestor(username = params['username'],
                                                  email = gae_user.email(),
                                                  credentials = google_id).put()
                result_user = {}
                result_user['username'] = params['username']
                result_user['status'] = 0
                result_user['logout_url'] = users.create_logout_url('/home')
                result_user['rank'] = 'Dora'
                self.build_base_response(status_code=201)
                self.response.out.write(json.dumps(result_user))
            else:
                self.abort(400)
        else:
            processed_params = self.validate_parameters_post(params)
            # Exchange the given authorization code for
            authorization_fields = {'code' : processed_params['authorization_code'],
                                    'client_id' : secrets.GOOGLE_APP_ID,
                                    'client_secret' : secrets.GOOGLE_APP_SECRET,
                                    'redirect_uri' : secrets.GOOGLE_REDIRECT_URI_ANDROID,
                                    'grant_type' : 'authorization_code'}
            result = urlfetch.fetch(url='https://accounts.google.com/o/oauth2/token',
                                    payload=urllib.urlencode(authorization_fields),
                                    method=urlfetch.POST,
                                    headers={'Content-Type': 'application/x-www-form-urlencoded'})
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
                                                         userkey=newuser.key.urlsafe(),
                                                         _full=True)}
                self.response.out.write(json.dumps(response_results))
            else:
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
