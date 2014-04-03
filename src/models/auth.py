'''Module that specifies several models that can be used as structured
properties to associate with user records.
'''
import base64
from datetime import datetime, timedelta
from google.appengine.ext import ndb
import time

from Crypto import Random

from models.general import GenericModel


class IdentityProvider(GenericModel):
    '''Top level identity provider, this defines the basic attributes and
    functionality of a IdentityProvider model.'''

    # : Unique id of the user given by the ID provider.
    user_id = ndb.StringProperty(required = True)
    # : Access token to call external APIs using the user's identity.
    access_token = ndb.StringProperty()
    # : Expiration time for the token
    expiration_time = ndb.DateTimeProperty()
    # : Name of the service, this should be overriden by subclasses.
    provider = ndb.StringProperty(default = 'Bogus')

    @classmethod
    def create_from_info(cls, auth_info, data):
        '''Method to create an :class:`IdentityProvider` object from the given
        authentication and user data. This is a generic method that should
        work for services with common callback responses.
        :returns: :class:`IdentityProvider` -- Credentials of the user in some 
                                               service.
        '''
        return None

    @classmethod
    def retrieve_email(cls, data):
        '''Method that returns the user's e-mail from the given user data. This
        is a generic method that should work for services with common data
        formats.
        :returns: str -- E-mail of the user in the service.
        '''
        return data['email']

class FacebookProvider(IdentityProvider):
    '''Facebook identity provider, service_name is facebook'''
    provider = ndb.StringProperty(default = 'facebook')

    @classmethod
    def create_from_info(cls, auth_info, data):
        '''Facebook-specific implementation of
        :py:meth:`IdentityProvider.create_from_info`'''
        return cls(user_id = data['id'],
                   access_token = auth_info['access_token'],
                   expiration_time = datetime.utcfromtimestamp(
                                time.time() + float(auth_info['expires'])))

class GoogleProvider(IdentityProvider):
    """Google identity provider, service_name is google."""
    provider = ndb.StringProperty(default = "google")
    refresh_token = ndb.StringProperty()

    @classmethod
    def create_from_info(cls, auth_info, data):
        '''Google-specific implementation of
        :py:meth:`IdentityProvider.create_from_info`'''
        return cls(user_id = data['id'],
                   access_token = auth_info['access_token'],
                   expiration_time = datetime.utcfromtimestamp(
                                time.time() + float(auth_info['expires_in'])))
    @classmethod
    def create_from_mobile(cls, auth_info):
        """Google-specific implementation of
        :py:meth:`IdentityProvider.create_from_mobile`"""
        return cls(user_id = auth_info['user_id'],
                   access_token = auth_info['access_token'],
                   refresh_token = auth_info['refresh_token'],
                   expiration_time = datetime.utcfromtimestamp(
                                time.time() + float(auth_info['expires_in'])))

class TwitterProvider(IdentityProvider):
    '''Twitter identity provider, service_name is twitter'''
    provider = ndb.StringProperty(default = 'twitter')

class LinkedinProvider(IdentityProvider):
    '''Linkedin identity provider, service_name is linkedin'''
    provider = ndb.StringProperty(default = 'linkedin2')

class SessionToken(GenericModel):
    """Session token model in the datastore."""
    _DEFAULT_EXPIRATION_TIME = 12 * 3600

    associated_user = ndb.KeyProperty(required = True)
    created_on = ndb.DateTimeProperty(auto_now_add = True)
    expires_on = ndb.ComputedProperty(lambda self : self.created_on +
                    timedelta(seconds = SessionToken._DEFAULT_EXPIRATION_TIME))
    token_hash = ndb.StringProperty(required = True)
    valid = ndb.BooleanProperty(default = True)

    @classmethod
    def create_token_for_user(cls, user):
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
    def invalidate_existing_tokens_for_user(cls, user):
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

# : Mapping from service name strings to the provider class
provider_map = {'facebook' : FacebookProvider,
                'google' : GoogleProvider,
                'twitter' : TwitterProvider,
                'linkedin2' : LinkedinProvider}
