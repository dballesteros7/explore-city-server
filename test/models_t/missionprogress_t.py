from google.appengine.api import files
from google.appengine.ext import ndb
import unittest

from xplore.database.models import Mission, MissionProgress, MissionWaypoint
from harness import TestHarness
from models_t.user_t import test_user


def create_blob(contents, mime_type):
    fn = files.blobstore.create(mime_type=mime_type)
    with files.open(fn, 'a') as f:
        f.write(contents)
    files.finalize(fn)
    return files.blobstore.get_blob_key(fn)

def test_waypoints():
    base_waypoint_name = 'waypoint%d'
    keys = []
    for i in xrange(5):
        blobkey = create_blob("Test-blob-not-really-an-image", 'application/octet-stream')
        location = ndb.GeoPt(i, i)
        waypoint = MissionWaypoint.create_with_default_ancestor(
                                                    name=base_waypoint_name % i,
                                                    location=location,
                                                    image=blobkey)
        waypoint.put()
        keys.append(waypoint.key)
    return keys

def test_mission():
    base_mission_name = 'mission'
    waypoint_keys = test_waypoints()
    mission = Mission.create_with_default_ancestor(name=base_mission_name,
                                                   waypoints=waypoint_keys)
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
        progress = MissionProgress(user=user.key,
                                   mission=mission.key)
        progress.start_mission()
        for waypoint in mission.waypoints:
            progress.complete_waypoint(waypoint)
        progress.finish_mission()
        print MissionProgress.get_all()

if __name__ == "__main__":
    unittest.main()
