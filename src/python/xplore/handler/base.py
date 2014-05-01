'''Base module for the Xplore web backend. 
It defines shared functionality with all webapp2 handlers.

.. moduleauthor:: Diego Ballesteros <diegob@student.ethz.ch>
'''
import webapp2
from webapp2_extras import sessions, jinja2

from xplore.database.models import AccessToken
from xplore.database.errors import ExpiredTokenError, InvalidTokenError, \
    NotExistentTokenError


class NoTokenError(Exception):
    pass

class NoUserError(Exception):
    pass

class BaseHandler(webapp2.RequestHandler):
    '''
    Base handler class for the project. It defines the basics of session
    management.
    '''

    def dispatch(self):
        # Get the session store for the request
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, _template, **context):
        # Renders a template and writes the result to the response.
        rv = self.jinja2.render_template(_template, **context)
        self.response.write(rv)

    def get_user(self, user_required=True):
        try:
            token_string = self.request.params['access_token']
            try:
                user = AccessToken.validate_token(token_string)
            except (InvalidTokenError,
                    ExpiredTokenError, NotExistentTokenError) as ex:
                if user_required:
                    raise ex
            return user
        except KeyError:
            raise NoTokenError()
