'''Module that handles the API for authentication with the server through OAuth
or OpenID.

.. moduleauthor:: Diego Ballesteros <diegob@student.ethz.ch>'''


import calendar
import json

from handler.api.base_service import BaseResource
from handler.auth import login_user
from handler.base import BaseHandler
from lib.simpleauth import SimpleAuthHandler
from models.auth import SessionToken
from models.user import TemporaryUser, User, NonExistentUserError
import secrets


class AuthHandler(SimpleAuthHandler, BaseHandler):
    '''Authentication handler that provides the API for authentication services
    in the server.
    '''
    # Extra secure (required for LinkedIn)
    OAUTH2_CSRF_STATE = True

    def _on_signin(self, data, auth_info, provider):
        '''Callback whenever a new or existing user is logging in.
        data is a user info dictionary.
        auth_info contains access token or oauth token and secret.
        See what's in it with logging.info(data, auth_info)'''

        # Create a temporary user
        tempuser = TemporaryUser.create_temporary_user(provider,
                                                       auth_info,
                                                       data)
        # Check if the user exists in the system
        realuser = User.check_user_existence(tempuser)
        if realuser is None:
            # The user has not registered his email and username
            # Prompt him to do it.
            # First store the user and retrieve the key.
            tempuser_key = tempuser.put()
            self.redirect(self.uri_for('login-page', tempuser_id = tempuser_key.urlsafe()))
        else :
            # User is already existence, then we can set the session.
            login_user(realuser, self.session)
            self.redirect('/')

    def logout(self):
        # logout_user(self.session)
        self.redirect('/')

    def _callback_uri_for(self, provider):
        return self.uri_for('auth_callback', provider = provider, _full = True)

    def _get_consumer_info_for(self, provider):
        '''Should return a tuple (key, secret) for auth init requests.
        For OAuth 2.0 you should also return a scope, e.g.
        ('my app id', 'my app secret', 'email,user_about_me')

        The scope depends solely on the provider.
        See example/secrets.py.template
        '''
        return secrets.AUTH_CONFIG[provider]


class TokenResource(BaseResource):
    """Resource class that handles the creation and invalidation of session
    tokens granted to the mobile app.
    """

    def get(self):
        """Retrieve a limited-life token for the given user, the required input
        is the username for identification and a JSON web token provided
        by the Google Auth API for security purposes.

        This invalidates any existing tokens in the datastore first, before
        issuing a new one.
        """
        # TODO: IMPLEMENT VALIDATION OF JSON WEB TOKEN FROM APP
        parameters = self.parse_request_body()
        the_user = User.get_by_username(parameters['username'])
        if the_user is None:
            raise NonExistentUserError(parameters['username'])
        SessionToken.invalidate_existing_tokens_for_user(the_user)
        token = SessionToken.create_token_for_user(the_user)
        self.build_base_response()
        response_body = {'access_token' : token.token_hash,
                         'expires_on' : calendar.timegm(token.expires_on.utctimetuple()),
                         'created_on' : calendar.timegm(token.created_on.utctimetuple()) }
        self.response.out.write(json.dumps(response_body))
