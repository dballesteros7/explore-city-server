from google.appengine.ext import ndb

from . import GenericModel


__all__ = ['MissionProgress']

class _MissionProgressEvent(GenericModel):
    timestamp = ndb.DateTimeProperty(auto_now_add=True)

class _MissionStarted(_MissionProgressEvent):
    description = ndb.StringProperty(default='Mission started')

class _WaypointCompleted(_MissionProgressEvent):
    description = ndb.StringProperty(default='Waypoint completed')
    waypoint = ndb.KeyProperty(kind='MissionWaypoint', required=True)

class _MissionFinished(_MissionProgressEvent):
    description = ndb.StringProperty(default='Mission finished')

class MissionProgress(GenericModel):
    """MissionProgress model that records the progress of an user in a given
    mission as a series of events.
    """

    user = ndb.KeyProperty(kind='User', required=True)
    mission = ndb.KeyProperty(kind='Mission', required=True)
    events = ndb.StructuredProperty(_MissionProgressEvent, repeated=True)

    def start_mission(self):
        start_event = _MissionStarted()
        self.events.append(start_event)
        self.put()

    def finish_mission(self):
        finish_event = _MissionFinished()
        self.events.append(finish_event)
        self.put()

    def complete_waypoint(self, waypoint):
        waypoint_complete_event = _WaypointCompleted(waypoint=waypoint)
        self.events.append(waypoint_complete_event)
        self.put()
