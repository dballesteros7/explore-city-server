import base64
from datetime import datetime, timedelta
from google.appengine.ext import ndb

from Crypto import Random

from . import GenericModel
from ..errors import ExpiredTokenError, InvalidTokenError, NotExistentTokenError


__all__ = ['AccessToken']

class AccessToken(GenericModel):
    """Access token ndb model"""

    _DEFAULT_ACCESS_TOKEN_ROOT = ndb.Key('AccessTokenRoot', 'default')
    _ACCESS_TOKEN_EXPIRATION_TIME = 24 * 3600
    _TOKEN_BYTE_LENGTH = 32

    associated_user = ndb.KeyProperty(kind='User', required=True)
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    expires_on = ndb.ComputedProperty(lambda self : self.created_on +
                  timedelta(seconds=AccessToken._ACCESS_TOKEN_EXPIRATION_TIME))
    token_string = ndb.StringProperty(required=True)
    valid = ndb.BooleanProperty(default=True)

    @classmethod
    def create(cls, user):
        """Create a new secure session token for the user, the token_string is
        generated as a 32-byte cryptographic-random sequence then
        encoded using base64 encoding.

        The token is stored as a valid token in the datastore before this
        method returns.

        Args:
            user: A valid instance of the User model.
        
        Returns:
            An instance of the SessionToken model, this represents the newly
            created token for the given user.
        """
        random_bytes = Random.get_random_bytes(AccessToken._TOKEN_BYTE_LENGTH)
        session_token = base64.b64encode(random_bytes)
        token = cls(parent=cls.default_ancestor(),
                    associated_user=user.key,
                    token_string=session_token)
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
                            ancestor=cls.default_ancestor())
        to_store = []
        for result in results:
            result.valid = False
            to_store.append(result)
        futures = []
        for result in to_store:
            futures.append(result.put_async())
        ndb.Future.wait_all(futures)

    @classmethod
    def validate_token(cls, query_token):
        """Verify if the given query_token matches a valid token in the
        database. A valid token must have the valid property set to True
        and have the expires_on property set after the current time.

        Args:
            query_token: Token to validate.

        Returns:
            Associated user key if the token matches a valid
            token.
        Raises:
            ExpiredTokenError -- if the given token is past expiration time.
            InvalidTokenError -- if the given token is invalid.
            NotExistentTokenError -- if the given token does not exist.
        """
        results = cls.query(cls.token_string == query_token,
                            ancestor=cls.default_ancestor())
        result = results.get()
        if result is not None:
            if not result.valid:
                raise InvalidTokenError()
            if result.expires_on <= datetime.utcnow():
                raise ExpiredTokenError()
            return result.associated_user
        else:
            raise NotExistentTokenError()
    
    @classmethod
    def default_ancestor(cls):
        return cls._DEFAULT_ACCESS_TOKEN_ROOT