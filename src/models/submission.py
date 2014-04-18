from google.appengine.ext import ndb

from models.general import GenericModel

class Submission(GenericModel):
    '''
    '''

    submitter = ndb.KeyProperty(required = True, kind = 'User')
    reference_mission = ndb.KeyProperty(required = True, kind = 'Mission')
    reference_waypoint = ndb.KeyProperty(required = True, kind = 'MissionWaypoint')
    submitted_image = ndb.BlobKeyProperty(required = True)
    created_on = ndb.DateTimeProperty(required = True, auto_now_add = True)
    score = ndb.FloatProperty(default = -1)