'''Module that defines the model for users in the datastore.

.. moduleauthor:: Diego Ballesteros <diegob@student.ethz.ch>
'''
from google.appengine.ext import ndb

from models.auth import IdentityProvider, provider_map
from models.general import GenericModel


_DEFAULT_USER_ROOT = ndb.Key('UserRoot', 'default')

class User(GenericModel):
    '''Model class that represents an user for the app.'''

    #: Represents the registered email for the user.
    email = ndb.StringProperty(required = True)
    #: Username that represents the user in the app.
    username = ndb.StringProperty(required = True)
    #: Flag that indicates if an user's email is already verified.
    mail_verified = ndb.BooleanProperty(default = False)
    #: Flag that indicates if the user is a registered administrator
    admin_status = ndb.BooleanProperty(default = False)
    #: Date when the user was created.
    created_time = ndb.DateTimeProperty(auto_now_add = True)
    #: Date when the user was last updated.
    updated_time = ndb.DateTimeProperty(auto_now = True)
    #: List of identity providers associated with the user.
    credentials = ndb.StructuredProperty(IdentityProvider, repeated = True)

    @classmethod
    def get_by_email(cls, email):
        '''Retrieves an user object given its unique email.

        :param email: E-mail for the query.
        :type email: str
        :returns: :class:`User` -- User object if found, None otherwise.
        '''
        query_result = cls.query(cls.email == email,
                                 ancestor = cls.default_ancestor()).fetch(1)
        if query_result:
            return query_result[0]
        else:
            return None

    @classmethod
    def check_user_existence(cls, tempuser):
        '''Verifies if the user exists given a tempuser with some credentials.
        
        :param tempuser: Temporary user holding credentials.
        :type tempuser: :class:`TemporaryUser`
        :returns: :class:`User` -- the matching user, None if none exists.
        '''
        import logging
        # Build a basic identity provider from the given user
        provider_class = provider_map[tempuser.credential.provider]
        logging.error(provider_class)
        stripped_tempuser = provider_class(user_id = tempuser.credential.user_id,
                                           provider = tempuser.credential.provider)
        logging.error(stripped_tempuser)
        # Query for the user_id
        query_result = cls.query(cls.credentials == stripped_tempuser,
                                 ancestor = cls.default_ancestor()).fetch(1)
        logging.error(query_result)
        if query_result:
            # If any user is found then return it
            return query_result[0]
        else:
            # Otherwise returns None
            return None

    @classmethod
    def create_user(cls, email, username, tempuser):
        '''Creates an user instance given an email and username, it doesn't
        store it on the datastore.

        :param email: Registered e-mail for the user.
        :type email: str
        :param username: Custom identifier for the user.
        :type username: str
        :param tempuser: Temporary user that holds credentials for the user.
        :type tempuser: :class:`TemporaryUser`
        :returns: :class:`User` -- the newly created user model.
        '''
        
        return cls(parent = cls.default_ancestor(),
                   email = email,
                   username = username,
                   credentials = [tempuser.credential])

    @classmethod
    def default_ancestor(cls):
        '''Override the default ancestor for user objects.

        :returns: :class:`ndb.Key` -- Default ancestor key.
        '''
        return _DEFAULT_USER_ROOT


class TemporaryUser(GenericModel):
    '''Model class that represents a signed in user that has not registered
    in the app.
    '''

    #: Credential object used to log in.
    credential = ndb.StructuredProperty(IdentityProvider, required = True)
    #: E-mail registered in the external service.
    suggested_email = ndb.StringProperty()
    #: Date when the user was created.
    created_time = ndb.DateTimeProperty(auto_now_add = True)
    #: Date when the user was last updated.
    updated_time = ndb.DateTimeProperty(auto_now = True)

    def delete(self):
        '''Delete itself.'''
        self.key.delete()

    @classmethod
    def create_temporary_user(cls, provider, auth_info, data):
        '''Creates a temporary user given the provider and the received auth
        information from the service along with the user's basic profile data.
        '''
        # First retrieve the appropriate identity provider to user.
        provider_class = provider_map[provider]
        # The class knows how to handle the data from the given provider.
        provider_obj = provider_class.create_from_info(auth_info, data)
        potential_email = provider_class.retrieve_email(data)
        # Now create the user with the given data.
        return cls(credential = provider_obj,
                   suggested_email = potential_email)

    @classmethod
    def default_ancestor(cls):
        '''Override the default ancestor for temporary user objects.

        :returns: :class:`ndb.Key` -- Default ancestor key.
        '''
        return _DEFAULT_USER_ROOT    