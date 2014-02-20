'''Module that defines the model for users in the datastore.

.. moduleauthor:: Diego Ballesteros <diegob@student.ethz.ch>
'''
from google.appengine.ext import ndb

from models.general import GenericModel

_DEFAULT_USER_ROOT = ndb.Key('UserRoot', 'default')

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
    #: Date when the user was created
    created_time = ndb.DateTimeProperty(auto_now_add = True)
    #: Date when the user was last updated
    updated_time = ndb.DateTimeProperty(auto_now = True)


    @classmethod
    def get_by_email(cls, email):
        '''Retrieves an user object given its unique email.
        :param email: E-mail for the query.
        :type email: str.
        :returns: :class:`User` -- User object if found, None otherwise.
        '''
        query_result = cls.query(cls.email == email,
                                 ancestor = cls.default_ancestor()).fetch(None)
        if query_result:
            return query_result[0]
        else:
            return None

    @classmethod
    def create_user(cls, email, username):
        '''Creates an user instance given an email and username, it doesn't
        store it on the datastore.

        :param email: Registered e-mail for the user.
        :type email: str.
        :param username: Custom identifier for the user.
        :type username: str.
        :returns: :class:`User` -- the newly created user model.
        '''
        return cls(parent = cls.default_ancestor(),
                   email = email,
                   username = username)

    @classmethod
    def default_ancestor(cls):
        '''Override the default ancestor for user objects.

        :returns: :class:`ndb.Key` -- Default ancestor key.
        '''
        return _DEFAULT_USER_ROOT

