'''
Model for a full mission in Google's NDB.
Created on Jan 7, 2014

@author: diegob
'''
from google.appengine.ext import ndb

from models.general import GenericModel
from models.missionwaypoint import MissionWaypoint


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
    startWaypoint = ndb.KeyProperty(kind = MissionWaypoint, required = True)
    waypoints = ndb.KeyProperty(kind = MissionWaypoint, repeated = True)

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
        qry = cls.query(cls.startWaypoint.IN(candidate_waypoints))
        results = qry.fetch(max_results)
        return results