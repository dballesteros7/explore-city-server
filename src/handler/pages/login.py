'''Module that provides the handlers for login pages in different scenarios.

.. moduleauthor:: Diego Ballesteros <diegob@student.ethz.ch>
'''
from handler.base import BaseHandler


class LoginPage(BaseHandler):
    '''Basic login page handler. It serves the initial login template with
    the different login options.
    '''

    def get(self):
        '''Return a page for login.
        '''
        self.render_response('login.html')