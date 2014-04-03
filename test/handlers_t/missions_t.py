
import unittest

from harness import TestHarnessWithWeb
from models.missionprogress import MissionProgress
from models_t.auth_t import test_token
from models_t.missionprogress_t import test_mission


class TestMissionResource(unittest.TestCase):


    def setUp(self):
        self.testharness = TestHarnessWithWeb()
        self.testharness.setup()


    def tearDown(self):
        self.testharness.destroy()


    def test_flow(self):
        token = test_token()
        mission = test_mission()
        resp = self.testharness.testapp.post('/api/missions/%s/start' % mission.key.string_id(),
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
                                                                                   waypoint.string_id()),
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
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
