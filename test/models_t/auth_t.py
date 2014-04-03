import unittest

from harness import TestHarness
from models.auth import GoogleIdentity, AccessToken
from models_t import user_t


class GoogleIdentityTest(unittest.TestCase):

    def setUp(self):
        self.testharness = TestHarness()
        self.testharness.setup()

    def tearDown(self):
        self.testharness.destroy()

    def test_create(self):
        """Simple test for creation of a GoogleIdentity instance."""
        mockup_auth_info = {'access_token':'1/fFAGRNJru1FTz70BzhT3Zg',
                            'refresh_token' : '2/fFAGRNJru1FTz80BzhT3Zg',
                            'expires_in':3920,
                            'token_type':'Bearer',
                            'user_gid' : '1234567890'}
        result = GoogleIdentity.create(mockup_auth_info)
        self.assertEqual(result.access_token, mockup_auth_info['access_token'])
        self.assertEqual(result.refresh_token, mockup_auth_info['refresh_token'])
        self.assertEqual(result.user_gid, mockup_auth_info['user_gid'])

class AccessTokenTest(unittest.TestCase):

    def setUp(self):
        self.testharness = TestHarness()
        self.testharness.setup()

    def tearDown(self):
        self.testharness.destroy()

    def test_create(self):
        """Simple test for creation of an AccessToken for an existing user."""
        test_user = user_t.test_user()
        token = AccessToken.create(test_user)
        self.assertEqual(len(AccessToken.query_all()), 1)
        self.assertEqual(token.associated_user, test_user.key)

    def test_invalidate(self):
        test_user = user_t.test_user()
        token = AccessToken.create(test_user)
        AccessToken.invalidate_tokens(test_user)
        token_2 = AccessToken.create(test_user)
        self.assertEqual(len(AccessToken.query_all()), 2)
        self.assertFalse(AccessToken.query_by_id(token.key.id())[0].valid)
        self.assertTrue(AccessToken.query_by_id(token_2.key.id())[0].valid)
        AccessToken.invalidate_tokens(test_user)
        self.assertFalse(any(t.valid for t in AccessToken.query_all()))

if __name__ == "__main__":
    unittest.main()
