'''
Module that defines the provider of the admin page.
Created on Jan 27, 2014

@author: diegob
'''

import os.path
import webapp2

from root import APPLICATION_ROOT


class AdminPage(webapp2.RequestHandler):
    '''
    Handler that provides the admin page on request.
    '''

    def get(self):
        '''
        GET verb for the handler which writes out the admin page defined in
        html/admin/admin.html
        '''
        self.response.write(open(os.path.join(APPLICATION_ROOT, 'html/admin/admin.html'), 'r').read())
