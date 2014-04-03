import unittest

from harness import TestHarness
from models.auth import AccessToken
from models_t import user_t

def test_token():
    user = user_t.test_user()
    token = AccessToken.create(user)
    return token

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

    def test_validate(self):
        test_user = user_t.test_user()
        token = AccessToken.create(test_user)
        self.assertEqual(AccessToken.validate_token(token.token_string),
                         test_user.key)
        AccessToken.invalidate_tokens(test_user)
        token_2 = AccessToken.create(test_user)
        self.assertFalse(AccessToken.validate_token(token.token_string))
        self.assertEqual(AccessToken.validate_token(token_2.token_string),
                         test_user.key)

if __name__ == "__main__":
    unittest.main()
