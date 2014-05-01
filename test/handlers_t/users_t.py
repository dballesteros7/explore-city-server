'''
Created on Apr 3, 2014

@author: diegob
'''
import unittest

from harness import TestHarnessWithWeb
from secrets_t import GOOGLE_USER_ID, GOOGLE_CODE
import xplore.secrets as secrets

class TestUsersResource(unittest.TestCase):

    def setUp(self):
        secrets.GOOGLE_REDIRECT_URI_ANDROID = secrets.GOOGLE_REDIRECT_URI
        self.testharness = TestHarnessWithWeb()
        self.testharness.setup()

    def tearDown(self):
        self.testharness.destroy()

    def test_post_get(self):
        # Enable only this test when needed.
        return
        username = 'testy'
        email = 'test@test.com'
        resp = self.testharness.testapp.post('/api/users', {'user_gid' : GOOGLE_USER_ID,
                                                            'authorization_code' : GOOGLE_CODE,
                                                            'username' : username,
                                                            'email' : email})
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.json['username'], username)
        userid = resp.json['content_url'].split('/')[-1]
        resp2 = self.testharness.testapp.get('/api/users/' + userid)
        self.assertEqual(resp2.status_int, 200)
        self.assertEqual(resp2.json['username'], username)
        self.assertEqual(resp2.json['email'], email)

if __name__ == "__main__":
    unittest.main()
