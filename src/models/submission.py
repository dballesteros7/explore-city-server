'''
Module that defines the model for submissions to the app.
Created on Jan 13, 2014

@author: diegob
'''
from google.appengine.ext import ndb

from models.general import GenericModel
from models.mission import Mission
from models.missionwaypoint import MissionWaypoint


class Submission(GenericModel):
    '''
    Submission model that represents an user submission for a waypoint
    in an specific mission. 
    Its key must register the User object as a parent for identification.
    '''

    reference_mission = ndb.KeyProperty(required = True, kind = Mission)
    reference_waypoint = ndb.KeyProperty(required = True, kind = MissionWaypoint)
    submitted_image = ndb.BlobKeyProperty(required = True)
    timestamp = ndb.DateTimeProperty(required = True)
    score = ndb.FloatProperty(default = -1)