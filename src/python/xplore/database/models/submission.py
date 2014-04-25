from google.appengine.ext import ndb

from . import  GenericModel
from geomodel import GeoModel


__all__ = ['UserSubmission']

class UserSubmission(GenericModel, GeoModel):

    owner = ndb.KeyProperty(kind = 'User', required = True)
    mission = ndb.KeyProperty(kind = 'Mission', required = True)
    waypoint = ndb.KeyProperty(kind = 'MissionWaypoint', required = True)
    image = ndb.BlobKeyProperty(required = True)
    created_on = ndb.DateTimeProperty(auto_now_add = True)
    score = ndb.FloatProperty(default = -1)