from google.appengine.ext import ndb
import json
import unittest

from xplore.database.models import MissionProgress, MissionWaypoint
from harness import TestHarnessWithWeb
from handlers_t.waypoints_t import create_blob
from models_t.auth_t import create_mock_token
from models_t.missionprogress_t import create_mock_mission


def create_mock_waypoints():
    base_waypoint_name = 'waypoint%d'
    waypoints = []
    for i in xrange(5):
        blobkey = create_blob('Test-blob-not-really-an-image',
                              'application/octet-stream')
        location = ndb.GeoPt(i, i)
        waypoint = MissionWaypoint.create_with_default_ancestor(
            name=base_waypoint_name % i,
            location=location,
            image=blobkey)
        waypoint.put()
        waypoints.append(waypoint)
    return waypoints


class TestMissionResource(unittest.TestCase):

    def setUp(self):
        self.testharness = TestHarnessWithWeb()
        self.testharness.setup()

    def tearDown(self):
        self.testharness.destroy()

    def test_single(self):
        waypoints = create_mock_waypoints()
        params = {'name': 'TestMission',
                  'waypoints': [w.name for w in waypoints]}
        resp = self.testharness.testapp.post('/api/missions',
                                             json.dumps(params),
                                             content_type='application/json')
        self.assertEqual(resp.status_int, 201)
        self.assertEqual(resp.json['name'], params['name'])
        resp2 = self.testharness.testapp.get(resp.json['content_url'])
        self.assertEqual(resp2.status_int, 200)
        self.assertEqual(len(resp2.json['missions']), 1)
        mission = resp2.json['missions'][0]
        self.assertEqual(mission['name'], params['name'])
        self.assertEqual(len(mission['waypoints']), len(params['waypoints']))

    def test_progress(self):
        token = create_mock_token()
        mission = create_mock_mission()
        resp = self.testharness.testapp.post('/api/missions/%s/start' % mission.name,
                                             {'access_token' : token.token_string})
        self.assertEqual(resp.status_int, 200)
        mission_progress_id = resp.json['mission_progress_id']
        mission_progress_model = MissionProgress.get_by_urlsafe(mission_progress_id)
        self.assertEqual(mission_progress_model.key.urlsafe(), mission_progress_id)
        self.assertEqual(len(mission_progress_model.events), 1)
        self.assertEqual(mission_progress_model.events[0].description, 'Mission started')
        self.assertEqual(mission_progress_model.mission, mission.key)

        count = 1
        for waypoint in mission.waypoints:
            count += 1
            resp = self.testharness.testapp.post('/api/missions/%s/complete/%s' % (mission_progress_id,
                                                                                   waypoint.get().name),
                                                 {'access_token' : token.token_string})
            self.assertEqual(resp.status_int, 200)
            mission_progress_model = MissionProgress.get_by_urlsafe(mission_progress_id)
            self.assertEqual(len(mission_progress_model.events), count)
            self.assertEqual(mission_progress_model.events[-1].description, 'Waypoint completed')
            self.assertEqual(mission_progress_model.events[-1].waypoint, waypoint)

        resp = self.testharness.testapp.post('/api/missions/%s/finish' % (mission_progress_id),
                                             {'access_token' : token.token_string})
        self.assertEqual(resp.status_int, 200)
        mission_progress_model = MissionProgress.get_by_urlsafe(mission_progress_id)
        self.assertEqual(len(mission_progress_model.events), count + 1)
        self.assertEqual(mission_progress_model.events[-1].description, 'Mission finished')

if __name__ == "__main__":
    unittest.main()
