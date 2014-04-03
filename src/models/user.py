'''Module that defines the model for users in the datastore.

.. moduleauthor:: Diego Ballesteros <diegob@student.ethz.ch>
'''
from google.appengine.ext import ndb

from models.auth import IdentityProvider, provider_map
from models.general import GenericModel


_DEFAULT_USER_ROOT = ndb.Key('UserRoot', 'default')

class ExistingUsernameError(Exception):
    """Exception that is triggered by attempting to create an user with
    an existing username.
    """

class EmailUsedError(Exception):
    """Exception that is triggered by attempting to create an user with an
    e-mail already registered by another user.
    """

class UnrecognizedServiceError(Exception):
    """Exception triggered by attempting to create an user with credentials
    provided by an unrecognized service.
    """

class ExistingUserError(Exception):
    """Exception triggered by an attempt to create an user with credentials
    already registered for another user.
    """

class NonExistentUserError(Exception):
    def __init__(self, username = None):
        self.username = username

class User(GenericModel):
    '''Model class that represents an user for the app.'''

    # : Represents the registered email for the user.
    email = ndb.StringProperty(required = True)
    # : Username that represents the user in the app.
    username = ndb.StringProperty(required = True)
    # : Flag that indicates if an user's email is already verified.
    mail_verified = ndb.BooleanProperty(default = False)
    # : Flag that indicates if the user is a registered administrator
    admin_status = ndb.BooleanProperty(default = False)
    # : Date when the user was created.
    created_time = ndb.DateTimeProperty(auto_now_add = True)
    # : Date when the user was last updated.
    updated_time = ndb.DateTimeProperty(auto_now = True)
    # : List of identity providers associated with the user.
    credentials = ndb.StructuredProperty(IdentityProvider, repeated = True)

    @classmethod
    def get_by_username(cls, username):
        """Retrieves an user object given its unique username.

        Args:
            username: Query username.

        Returns:
            A matching user object if any exists, None otherwise.
        """
        query_result = cls.query(cls.username == username,
                                 ancestor = cls.default_ancestor()).fetch(1)
        if query_result:
            return query_result[0]
        else:
            return None

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
    def check_user_existence_for_mobile(cls, provider, user_id):
        '''Verifies if the user exists given a provider and its id in such
        provider.
        '''
        provider_class = provider_map[provider]
        credential = provider_class(user_id = user_id,
                                    provider = provider)
        return cls.check_user_existence(credential)

    @classmethod
    def check_user_existence(cls, credential):
        """Verifies if the user exists given some credentials.

        Args:
            credential: Object holding the credentials for the user, this
                must be a valid descendant from the IdentityProvider class.

        Returns:
            A matching user object if such exists, None otherwise.
        """
        provider_class = provider_map[credential.provider]
        stripped_credential = provider_class(user_id = credential.user_id,
                                             provider = credential.provider)
        query_result = cls.query(cls.credentials == stripped_credential,
                                 ancestor = cls.default_ancestor()).fetch(1)
        if query_result:
            return query_result[0]
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
    def create_user_from_mobile(cls, email, username, put = True, **auth_info):
        """Creates an user instance given its email, username and a dictionary
        with its auth info.

        Args:
            email: Registered e-mail for the user.
            username: Custom identifier for the user.
            put: If true then the user object will be stored synchronously in
                the datastore. True by default.
            **auth_info: Dictionary with authentication information, this must
                contain at least the 'service' key, plus the arguments required
                by the IdentityProvider class-specific constructor for that
                service.

        Returns:
            The newly created user instance.

        Raises:
            ExistingUsernameError: If there's already an user with
                the given username.
            EmailUsedError: If there's already an user with the given e-mail
                registered.
            UnrecognizedServiceError: If there's no IdentityProvider for the
                given service name.
        """
        provider = auth_info['provider']
        try:
            provider_class = provider_map[provider]
        except KeyError:
            raise UnrecognizedServiceError()
        provider_obj = provider_class.create_from_mobile(auth_info)

        if cls.check_user_existence(provider_obj) is not None:
            raise ExistingUserError()
        if cls.get_by_username(username) is not None:
            raise ExistingUsernameError()
        if cls.get_by_email(email) is not None:
            raise EmailUsedError()

        user_object = cls(parent = cls.default_ancestor(),
                          username = username,
                          email = email,
                          credentials = [provider_obj])
        if put:
            user_object.put()
        return user_object

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

    # : Credential object used to log in.
    credential = ndb.StructuredProperty(IdentityProvider, required = True)
    # : E-mail registered in the external service.
    suggested_email = ndb.StringProperty()
    # : Date when the user was created.
    created_time = ndb.DateTimeProperty(auto_now_add = True)
    # : Date when the user was last updated.
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
