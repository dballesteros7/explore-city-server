from google.appengine.api.images import get_serving_url
from google.appengine.ext import ndb
from google.appengine.ext.blobstore import BlobInfo

from geomodel import GeoModel
from geotypes import Box
from xplore.database.utils import get_missions_for_waypoint

from . import GenericModel

__all__ = ['MissionWaypoint']


class MissionWaypoint(GenericModel, GeoModel):
    """Waypoint model.

    Properties:
    * name: Name of the waypoint, unique across the namespace. This is the only
        required argument
    * image: Key for the waypoint image stored in the Blobstore.
    * image_url: URL pointing to the image, this can be provided in place of
        image.
    * description: Description of the waypoint, if any.
    * tags: List of tags associated with the waypoint.
    * created_by: Creator of the waypoint. This points to a valid user
        in the system.
    * created_on: Date when the waypoint was created in the system.
    * difficulty: Difficulty scale for the waypoint.
    """
    _DEFAULT_MISSION_WAYPOINT_ROOT = ndb.Key('MissionWaypointRoot', 'default')

    name = ndb.StringProperty(required=True)
    image = ndb.BlobKeyProperty()
    image_url = ndb.StringProperty()
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

    def delete(self):
        related_missions = get_missions_for_waypoint(self.key)
        map(lambda x: x.remove_waypoint(self.key), related_missions)
        BlobInfo.get(self.image).delete()
        self.key.delete()

    def to_jsonizable(self, image_size):
        result = {'latitude': self.location.lat,
                  'longitude': self.location.lon,
                  'name': self.name}
        if self.image is not None:
            result['image_url'] = get_serving_url(self.image, size=image_size)
            result['image_key'] = str(self.image)
        elif self.image_url is not None:
            result['image_url'] = self.image_url
        return result
