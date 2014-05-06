from google.appengine.ext import ndb
from google.appengine.ext.ndb.blobstore import BlobInfo

from geo.geomodel import GeoModel
from geo.geotypes import Box

from general import GenericModel


__all__ = ['MissionWaypoint']

class MissionWaypoint(GenericModel, GeoModel):
    """
    A mission waypoint model.

    Properties:
    - name*: Name of the waypoint, unique across the namespace.
    - image*: Key for the waypoint image stored in the Blobstore.
    - description: Description of the waypoint, if any.
    - tags: List of tags associated with the waypoint.
    - created_by: Creator of the waypoint. This points to a valid user
        in the system.
    - created_on: Date when the waypoint was created in the system.
    - difficulty: Difficulty scale for the waypoint.
    - location**: Location of the waypoint, stored as a lat,long GeoPtProperty.
    - location_geocells**: Encoded location as geocells.

    * Required property.
    ** Property inherited from GeoModel.
    """
    _DEFAULT_MISSION_WAYPOINT_ROOT = ndb.Key('MissionWaypointRoot', 'default')

    name = ndb.StringProperty(required = True)
    image = ndb.BlobKeyProperty(required=True)
    description = ndb.StringProperty()
    tags = ndb.StringProperty(repeated=True)
    created_by = ndb.KeyProperty(kind='User')
    created_on = ndb.DateProperty(auto_now_add=True)
    difficulty = ndb.StringProperty(choices=['Easy', 'Medium', 'Hard',
                                               'Xplorer'])

    @classmethod
    def query_near(cls, center, max_results=None, max_distance=0):
        if max_results is None:
            max_results = cls._MAX_QUERY_RESULTS
        base_query = cls.query()
        results = cls.proximity_fetch(base_query, center,
                                      max_results, max_distance)
        return results

    @classmethod
    def query_box(cls, north, east, south, west, max_results=None):
        if max_results is None:
            max_results = cls._MAX_QUERY_RESULTS
        query_box = Box(north, east, south, west)
        base_query = cls.query()
        results = cls.bounding_box_fetch(base_query, query_box, max_results)
        return results

    @classmethod
    def default_ancestor(cls):
        return cls._DEFAULT_MISSION_WAYPOINT_ROOT
