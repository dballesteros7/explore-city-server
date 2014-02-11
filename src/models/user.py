'''
Module that defines the model for users in the datastore.

.. moduleauthor:: Andrew Carter <andrew@invalid.com>

Created on Jan 13, 2014

@author: diegob
'''
from google.appengine.ext import ndb

from models.general import GenericModel


class User(GenericModel):
    '''
    Model class that represents an user for the app.
    '''

    #: Represents the registered email for the user
    email = ndb.StringProperty(required = True)
    #: Username that represents the user in the app
    username = ndb.StringProperty(required = True)
    #: Flag that indicates if an user's email is already verified
    mail_verified = ndb.BooleanProperty(default = False)
    #: Unique ID provided by Google login service
    google_id = ndb.StringProperty()

    @classmethod
    def create_user(cls, email, username):
        '''Creates an user instance given an email and username, it doesn't
        store it on the datastore.

        :param email: Registered e-mail for the user.
        :type email: str.
        :param username: Custom identifier for the user.
        :type username: str.
        :returns: User -- the newly created user model.
        '''
        return cls(email = email,
                   username = username)

