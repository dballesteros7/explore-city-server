'''
Module that defines the model for users in the datastore.
Created on Jan 13, 2014

@author: diegob
'''
from google.appengine.ext import ndb

from models.general import GenericModel


class User(GenericModel):
    '''
    Model class that represents an user for the app.
    '''

    email = ndb.StringProperty(required = True)
    nickname = ndb.StringProperty()