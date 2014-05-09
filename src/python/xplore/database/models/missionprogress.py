from google.appengine.ext import ndb

from . import GenericModel


__all__ = ['MissionProgress']

class _MissionProgressEvent(GenericModel):
    description = ndb.StringProperty()
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    waypoint = ndb.KeyProperty()
    
    def to_json(self):
        json_self = {'timestamp' : self.timestamp.isoformat()}
        if self.description:
            json_self['description'] = self.description
        else:
            json_self['description'] = ''
        if self.waypoint:
            json_self['waypoint'] = self.waypoint.urlsafe()
        else:
            json_self['waypoint'] = None
        return json_self

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

    @classmethod
    def statistics_for_user_and_waypoint(cls, user_key, waypoint_key):
        qry = cls.query(cls.user == user_key,
                      cls.events.waypoint == waypoint_key)
        return qry.fetch()

    @classmethod
    def visits_for_waypoint(cls, waypoint_key):
        qry = cls.query(cls.events.waypoint == waypoint_key)
        results =  qry.fetch()
        events = []
        for result in results:
            for event in result.events:
                if getattr(event, 'waypoint', None):
                    events.append(event)
        return events

    def to_json(self):
        json_self = {'user' : self.user.urlsafe(),
                     'mission' : self.user.urlsafe(),
                     'events' : [e.to_json() for e in self.events]}
        return json_self
