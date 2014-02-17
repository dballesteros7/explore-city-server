'''Module that defines some functions to ensure authentication when requesting
methods to the server.
Created on Feb 13, 2014

@author: diegob
'''

from google.appengine.api import users

from models.user import User


def login_required(handler):
    '''Decorator that checks that an user is logged in before executing the
    given handler method.
    '''
    def check_login(self, *args, **kwargs):
        user = users.get_current_user()
        if user:
            if User.get_by_email(user.email()) is not None:
                return handler(self, *args, **kwargs)
            else:
                self.redirect(self.uri_for('login-page'), abort = True)
        else:
            self.redirect(self.uri_for('login-page'), abort = True)
    return check_login
