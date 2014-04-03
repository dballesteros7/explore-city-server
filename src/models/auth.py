import base64
from datetime import datetime, timedelta
from google.appengine.ext import ndb
import time

from Crypto import Random

from models.general import GenericModel

_ACCESS_TOKEN_EXPIRATION_TIME = 12 * 3600

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
                                time.time() + float(auth_info['expires_in'])))

class AccessToken(GenericModel):
    """Access token model in the datastore."""

    associated_user = ndb.KeyProperty(required = True)
    created_on = ndb.DateTimeProperty(auto_now_add = True)
    expires_on = ndb.ComputedProperty(lambda self : self.created_on +
                    timedelta(seconds = _ACCESS_TOKEN_EXPIRATION_TIME))
    token_hash = ndb.StringProperty(required = True)
    valid = ndb.BooleanProperty(default = True)

    @classmethod
    def create(cls, user):
        """Create a new secure session token for the user, the token_hash is
        generated as a 32-byte cryptographically-strong random sequence then
        encoded using a base 64 encoding.

        The token is stored as a valid token in the datastore before this
        method returns.
        
        Args:
            user: A valid instance of the User model.
        
        Returns:
            An instance of the SessionToken model, this represents the newly
            created token for the given user.
        """
        random_bytes = Random.get_random_bytes(32)
        session_token = base64.b64encode(random_bytes)
        token = cls(parent = cls.default_ancestor(),
                    associated_user = user.key,
                    token_hash = session_token)
        token.put()
        return token

    @classmethod
    def invalidate_tokens(cls, user):
        """Invalidate any previous valid tokens for the given user in the
        datastore, this is done by setting the valid attribute to false.

        Args:
            user: A valid instance of the User model.
        """
        results = cls.query(cls.associated_user == user.key,
                            cls.valid == True,
                            ancestor = cls.default_ancestor())
        to_store = []
        for result in results:
            result.valid = False
            to_store.append(result)
        for result in to_store:
            result.put()
