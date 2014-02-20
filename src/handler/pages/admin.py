'''
Module that defines the provider of the admin page.
Created on Jan 27, 2014

@author: diegob
'''

import os.path

from root import APPLICATION_ROOT
from handler.auth import login_required
from handler.base import BaseHandler


class AdminPage(BaseHandler):
    '''
    Handler that provides the admin page on request.
    '''

    @login_required(admin_only = True)
    def get(self):
        '''
        GET verb for the handler which writes out the admin page defined in
        html/admin/admin.html
        '''
        self.response.write(open(os.path.join(APPLICATION_ROOT, 'html/admin/admin.html'), 'r').read())
