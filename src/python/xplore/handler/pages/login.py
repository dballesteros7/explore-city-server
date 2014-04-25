'''Module that provides the handlers for login pages in different scenarios.

.. moduleauthor:: Diego Ballesteros <diegob@student.ethz.ch>
'''
from google.appengine.ext import ndb

from xplore.handler.base import BaseHandler


class LoginPage(BaseHandler):
    '''Basic login page handler. It serves the initial login template with
    the different login options.'''

    def get(self):
        '''Return a page for login.'''
        context = {}
        user_url = self.session.get('_user_id', None)
        tempuser_url = self.request.get('tempuser_id', None)
        if user_url is not None:
            # The user is already logged in.
            context['logged_in'] = True
            context['username'] = ndb.Key(urlsafe = user_url).get().username
        elif tempuser_url is not None:
            # If there is a tempuser id then the user is in the second step
            # of the login process. Provide the appropriate page for it.
            # First retrieve the temporary user instance.
            tempuser_key = ndb.Key(urlsafe = tempuser_url)
            tempuser = tempuser_key.get()
            context['suggested_email'] = tempuser.suggested_email
            context['provider'] = tempuser.credential.provider
            context['user_key'] = tempuser_url
            context['second_step'] = True
            context['user_registration_url'] = self.uri_for('users-resource')
        else:
            context['second_step'] = False
        self.render_response('login.html', **context)