from datetime import datetime
from google.appengine.ext import ndb
from time import time

from . import GenericModel

__all__ = ['GoogleIdentity', 'User']

class ExistingUsernameError(Exception):
    """Exception that is triggered by attempting to create an user with
    an existing username.
    """

class ExistingEmailError(Exception):
    """Exception that is triggered by attempting to create an user with an
    e-mail already registered by another user.
    """

class ExistingGoogleIdError(Exception):
    """Exception triggered by an attempt to create an user with credentials
    already registered for another user.
    """

class NonExistentUserError(Exception):
    """Exception triggered when a non-existent user is requested from the
    datastore.
    """

class GoogleIdentity(GenericModel):
    """Google identity provider, this model functions as an StructuredProperty
    for the User model. It stores the credentials necessary for using the
    Google APIs on behalf of the user."""

    user_gid = ndb.StringProperty(required = True)
    access_token = ndb.StringProperty(required = True)
    refresh_token = ndb.StringProperty(required = True)
    expiration_time = ndb.DateTimeProperty(required = True)

    @classmethod
    def create(cls, auth_info):
        """Method to create a new instance containing the credentials of an
        user in Google.
        
        Args:
            auth_info: Dict with the credentials of the user in google, it
            requires the following keys:
                * user_gid -- The user's Google id.
                * access_token -- Short-lived access token for the user.
                * refresh_token -- Long-lived token to request new access
                                   tokens.
                * expires_in -- Time until expiration of the access token.

        Returns:
            Instance of the GoogleIdentity model with the given credentials.
        """
        return cls(user_gid = auth_info['user_gid'],
                   access_token = auth_info['access_token'],
                   refresh_token = auth_info['refresh_token'],
                   expiration_time = datetime.utcfromtimestamp(
                                time() + float(auth_info['expires_in'])))

class User(GenericModel):
    """Model class that represents an user for the app."""

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
    # : Credentials of the user in the app.
    credentials = ndb.StructuredProperty(GoogleIdentity)

    @classmethod
    def get_by_username(cls, username):
        """Retrieves an user object given its unique username.

        Args:
            username: Query username.

        Returns:
            A matching user object if any exists, None otherwise.
        """
        query_result = cls.query(cls.username == username,
                                 ancestor = cls.default_ancestor()).get()
        return query_result

    @classmethod
    def get_by_email(cls, email):
        """Retrieves an user object given its unique email.

        Args:
            email: Query e-mail.
        
        Returns:
            A matching user object if any exists, None otherwise.
        """
        query_result = cls.query(cls.email == email,
                                 ancestor = cls.default_ancestor()).get()
        return query_result

    @classmethod
    def get_by_google_id(cls, user_gid):
        """Retrieves an user object given its unique Google id.

        Args:
            user_gid: Query Google id.

        Returns:
            A matching user object if any exists, None otherwise.
        """
        query_result = cls.query(cls.credentials.user_gid == user_gid,
                                 ancestor = cls.default_ancestor()).get()
        return query_result

    @classmethod
    def create(cls, email, username, auth_info):
        """Creates an user instance given its email, username and a dictionary
        with its auth info, and stores it in the datastore.

        Args:
            email: Registered e-mail for the user.
            username: Custom identifier for the user.
            auth_info: Dictionary with authentication information, this must
            contain the keys required in the GoogleIdentity created method.

        Returns:
            The newly created user instance.

        Raises:
            ExistingUsernameError: If there's already an user with
                the given username.
            EmailUsedError: If there's already an user with the given e-mail
                registered.
        """

        if cls.get_by_google_id(auth_info['user_gid']) is not None:
            raise ExistingGoogleIdError()
        if cls.get_by_username(username) is not None:
            raise ExistingUsernameError()
        if cls.get_by_email(email) is not None:
            raise ExistingEmailError()

        google_credentials = GoogleIdentity.create(auth_info)
        user_object = cls(parent = cls.default_ancestor(),
                          username = username,
                          email = email,
                          credentials = google_credentials)
        user_object.put()
        return user_object