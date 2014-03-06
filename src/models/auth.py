'''Module that specifies several models that can be used as structured
properties to associate with user records.
'''
import time
from datetime import datetime
from google.appengine.ext import ndb

from models.general import GenericModel


class IdentityProvider(GenericModel):
    '''Top level identity provider, this defines the basic attributes and
    functionality of a IdentityProvider model.'''
    
    #: Unique id of the user given by the ID provider.
    user_id = ndb.StringProperty(required = True)
    #: Access token to call external APIs using the user's identity.
    access_token = ndb.StringProperty(indexed = False)
    #: Expiration time for the token
    expiration_time = ndb.DateTimeProperty()
    #: Name of the service, this should be overriden by subclasses.
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
    '''Google identity provider, service_name is google'''
    provider = ndb.StringProperty(default = 'google')

    @classmethod
    def create_from_info(cls, auth_info, data):
        '''Google-specific implementation of
        :py:meth:`IdentityProvider.create_from_info`'''
        return cls(user_id = data['id'],
                   access_token = auth_info['access_token'],
                   expiration_time = datetime.utcfromtimestamp(
                                time.time() + float(auth_info['expires_in'])))

class TwitterProvider(IdentityProvider):
    '''Twitter identity provider, service_name is twitter'''
    provider = ndb.StringProperty(default = 'twitter')

class LinkedinProvider(IdentityProvider):
    '''Linkedin identity provider, service_name is linkedin'''
    provider = ndb.StringProperty(default = 'linkedin2')

#: Mapping from service name strings to the provider class
provider_map = {'facebook' : FacebookProvider,
                'google' : GoogleProvider,
                'twitter' : TwitterProvider,
                'linkedin2' : LinkedinProvider}