'''Module that contains the login pages
Created on Feb 13, 2014

@author: diegob
'''
from google.appengine.api import users

import webapp2


class LoginPage(webapp2.RequestHandler):
    '''
    classdocs
    '''
    
    def get(self):
        '''Return a page for login.
        '''
        greeting = ('<a href="%s">Sign in or register</a>.' %
                    users.create_login_url('/admin'))
        self.response.out.write('<html><body>%s</body></html>' % greeting)