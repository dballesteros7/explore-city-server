from google.appengine.api import files
import unittest

from geocell.geopoint import GeoPoint as BaseGeoPoint
from harness import TestHarness
from models.geopoint import GeoPoint
from models.mission import Mission
from models.missionprogress import MissionProgress
from models.missionwaypoint import MissionWaypoint
from models_t.user_t import test_user


def create_blob(contents, mime_type):
    fn = files.blobstore.create(mime_type = mime_type)
    with files.open(fn, 'a') as f:
        f.write(contents)
    files.finalize(fn)
    return files.blobstore.get_blob_key(fn)

def test_waypoints():
    base_waypoint_name = 'waypoint%d'
    keys = []
    for i in xrange(5):
        blobkey = create_blob("Test-blob-not-really-an-image", 'application/octet-stream')
        location = GeoPoint.from_geocell_point(BaseGeoPoint(i, i, 12))
        waypoint = MissionWaypoint.build(id = base_waypoint_name % i,
                              location = location,
                              reference_image = blobkey)
        waypoint.put()
        keys.append(waypoint.key)
    return keys

def test_mission():
    base_mission_name = 'mission'
    waypoint_keys = test_waypoints()
    mission = Mission.build(id = base_mission_name,
                  start_waypoint = waypoint_keys[0],
                  waypoints = waypoint_keys)
    mission.put()
    return mission

class MissionProgressTest(unittest.TestCase):


    def setUp(self):
        self.testharness = TestHarness()
        self.testharness.setup()


    def tearDown(self):
        self.testharness.destroy()


    def test_flow(self):
        mission = test_mission()
        user = test_user()
        progress = MissionProgress(user = user.key,
                                   mission = mission.key)
        progress.start_mission()
        for waypoint in mission.waypoints:
            progress.complete_waypoint(waypoint)
        progress.finish_mission()
        print MissionProgress.query_all()

if __name__ == "__main__":
    unittest.main()
