import base64
from datetime import timedelta
from google.appengine.ext import ndb

from Crypto import Random

from models.general import GenericModel


_ACCESS_TOKEN_EXPIRATION_TIME = 24 * 3600 # 12h tokens
_TOKEN_BYTE_LENGTH = 32

class AccessToken(GenericModel):
    """Access token model in the datastore."""

    associated_user = ndb.KeyProperty(kind = 'User', required = True)
    created_on = ndb.DateTimeProperty(auto_now_add = True)
    expires_on = ndb.ComputedProperty(lambda self : self.created_on +
                    timedelta(seconds = _ACCESS_TOKEN_EXPIRATION_TIME))
    token_string = ndb.StringProperty(required = True)
    valid = ndb.BooleanProperty(default = True)

    @classmethod
    def create(cls, user):
        """Create a new secure session token for the user, the token_string is
        generated as a 32-byte cryptographic-strong random sequence then
        encoded using a base 64 encoding.

        The token is stored as a valid token in the datastore before this
        method returns.
        
        Args:
            user: A valid instance of the User model.
        
        Returns:
            An instance of the SessionToken model, this represents the newly
            created token for the given user.
        """
        random_bytes = Random.get_random_bytes(_TOKEN_BYTE_LENGTH)
        session_token = base64.b64encode(random_bytes)
        token = cls(parent = cls.default_ancestor(),
                    associated_user = user.key,
                    token_string = session_token)
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

    @classmethod
    def validate_token(cls, query_token):
        """Verify if a token exists given its random string and
        retrieve the associated user key.
        
        Args:
            query_token: Token hash to validate.
        
        Returns:
            Associated user key if the token matches an existing valid
            token, None otherwise.
        """
        results = cls.query(cls.token_string == query_token,
                            cls.valid == True,
                            ancestor = cls.default_ancestor())
        result = results.get()
        if result is not None:
            return result.associated_user
        return None
