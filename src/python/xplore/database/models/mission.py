from google.appengine.ext import ndb

from . import GenericModel


__all__ = ['Mission']

class Mission(GenericModel):

    _DEFAULT_MISSION_ROOT = ndb.Key('MissionRoot', 'default')

    name = ndb.StringProperty(required = True)
    waypoints = ndb.KeyProperty(kind = 'MissionWaypoint', repeated = True)
    description = ndb.StringProperty()
    tags = ndb.StringProperty(repeated=True)
    created_by = ndb.KeyProperty(kind='User')
    created_on = ndb.DateProperty(auto_now_add=True)
    distance = ndb.FloatProperty()
    expected_duration = ndb.FloatProperty()

    @classmethod
    def query_by_waypoint(cls, candidate_waypoints,
                          max_results=None):
        '''
        Query for missions given some waypoints keys, missions which have any
        of the waypoints as starting points will be returned.
        '''
        if max_results is None:
            max_results = cls._MAX_QUERY_RESULTS
        if isinstance(candidate_waypoints, ndb.Key):
            candidate_waypoints = [candidate_waypoints]
        qry = cls.query(cls.waypoints.IN(candidate_waypoints),
                        ancestor = cls.default_ancestor())
        results = qry.fetch(max_results)
        return results

    @classmethod
    def default_ancestor(cls):
        '''
        Override the default ancestor for missions.
        '''
        return cls._DEFAULT_MISSION_ROOT

    def remove_waypoint(self, waypoint_key):
        self.waypoints.remove(waypoint_key)
        if len(self.waypoints):
            self.start_waypoint = self.waypoints[0]
            self.put()
        else:
            self.delete()