import unittest

from xplore.database.models import AccessToken
from xplore.database.models.auth import _ACCESS_TOKEN_EXPIRATION_TIME
from harness import TestHarnessWithWeb
from models_t.user_t import test_user


class TokenResourceTest(unittest.TestCase):

    def setUp(self):
        self.testharness = TestHarnessWithWeb()
        self.testharness.setup()

    def tearDown(self):
        self.testharness.destroy()

    def test_grant_token(self):
        the_user = test_user()
        resp = self.testharness.testapp.get('/auth/token',
                                            {'username' : the_user.username})
        self.assertEqual(resp.status_int, 200)
        json_resp = resp.json
        single_token = AccessToken.get_all(1)[0]
        self.assertEqual(json_resp['access_token'], single_token.token_string)
        self.assertEqual(json_resp['expires_on'] - json_resp['created_on'],
                         _ACCESS_TOKEN_EXPIRATION_TIME)
        resp = self.testharness.testapp.get('/auth/token',
                                            {'username' : the_user.username})
        self.assertEqual(resp.status_int, 200)
        json_resp_2 = resp.json
        self.assertNotEqual(json_resp['access_token'], json_resp_2['access_token'])
        tokens = AccessToken.get_all()
        self.assertEqual(sum(t.valid for t in tokens), 1)

if __name__ == "__main__":
    unittest.main()