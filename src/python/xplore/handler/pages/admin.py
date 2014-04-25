'''
Module that defines the provider of the admin page.
Created on Jan 27, 2014

@author: diegob
'''

from xplore.handler.auth import login_required
from xplore.handler.base import BaseHandler

class AdminPage(BaseHandler):
    '''
    Handler that provides the admin page on request.
    '''

    @login_required(admin_only = True)
    def get(self):
        '''
        GET verb for the handler which writes out the admin page defined in
        templates/admin.html
        '''
        context = {}
        self.render_response('admin.html', **context)
