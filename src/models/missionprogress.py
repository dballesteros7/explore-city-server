from google.appengine.ext import ndb

from models.general import GenericModel


class MissionProgressEvent(GenericModel):
    timestamp = ndb.DateTimeProperty(required = True, auto_now_add = True)

class MissionStarted(MissionProgressEvent):
    description = ndb.StringProperty(default = 'Mission started')

class WaypointCompleted(MissionProgressEvent):
    description = ndb.StringProperty(default = 'Waypoint completed')
    waypoint = ndb.KeyProperty(kind = 'MissionWaypoint', required = True)

class MissionFinished(MissionProgressEvent):
    description = ndb.StringProperty(default = 'Mission finished')

class MissionProgress(GenericModel):
    """MissionProgress model that records the progress of an user in a given
    mission as a series of events.
    """

    user = ndb.KeyProperty(kind = 'User', required = True)
    mission = ndb.KeyProperty(kind = 'Mission')
    events = ndb.StructuredProperty(MissionProgressEvent, repeated = True)

    def start_mission(self):
        start_event = MissionStarted()
        self.events.append(start_event)
        self.put()

    def finish_mission(self):
        finish_event = MissionFinished()
        self.events.append(finish_event)
        self.put()

    def complete_waypoint(self, waypoint):
        waypoint_complete_event = WaypointCompleted(waypoint = waypoint)
        self.events.append(waypoint_complete_event)
        self.put()
