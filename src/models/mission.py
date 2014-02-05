'''
Model for a full mission in Google's NDB.
Created on Jan 7, 2014

@author: diegob
'''
from google.appengine.ext import ndb

from models.general import GenericModel

_DEFAULT_MISSION_ROOT = ndb.Key('MissionRoot', 'default')

class Mission(GenericModel):
    '''
    A mission is a named ordered list of waypoints. In the context
    of the game it is meant to contain waypoints which are mean to be visited
    together in sequence, i.e. a collection of churches around Zurich.

    Currently, a mission is just a name and a list of NDB keys pointing
    to MissionWaypoint entities.

    Missions can be queried based on location and this query is matched
    against the mission's starting point. Otherwise, queries will be done
    by name.
    '''

    ##############
    # Properties #
    ##############
    start_waypoint = ndb.KeyProperty(kind = 'MissionWaypoint', required = True)
    waypoints = ndb.KeyProperty(kind = 'MissionWaypoint', repeated = True)

    ###########################################################################
    # Model methods
    ###########################################################################
    def remove_waypoint(self, waypointKey):
        '''
        Delete the given waypoint from the mission.
        This method assumes that the waypoint exists in the mission. It
        expects a waypoint key as argument.
        '''
        self.waypoints.remove(waypointKey)
        if len(self.waypoints):
            self.start_waypoint = self.waypoints[0]
            self.put()
        else:
            self.delete()

    def delete(self):
        '''
        Delete the given mission from the datastore.
        '''
        self.key.delete()

    ###########################################################################
    # Custom constructors
    ###########################################################################
    @classmethod
    def build(cls, **kwargs):
        '''
        Create an instance of the mission class with the default ancestor in
        the key.
        '''
        return cls(parent = cls.default_ancestor(),
                   **kwargs)
    ##############
    # Queries    #
    ##############
    @classmethod
    def query_by_waypoint(cls, candidate_waypoints, max_results):
        '''
        Query for missions given some waypoints keys, missions which have any
        of the waypoints as starting points will be returned.
        '''
        if max_results is None:
            max_results = cls.MAX_QUERY_RESULTS
        qry = cls.query(cls.start_waypoint.IN(candidate_waypoints),
                        ancestor = cls.default_ancestor())
        results = qry.fetch(max_results)
        return results

    @classmethod
    def query_contains_waypoint(cls, waypoint_key):
        '''
        Query for missions that contain the given waypoint at any position
        in the mission.
        '''
        qry = cls.query(cls.waypoints == waypoint_key,
                        ancestor = cls.default_ancestor());
        return qry.fetch();

    @classmethod
    def default_ancestor(cls):
        '''
        Override the default ancestor for missions.
        '''
        return _DEFAULT_MISSION_ROOT