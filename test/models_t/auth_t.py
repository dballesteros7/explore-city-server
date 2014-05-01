import time
import unittest

from harness import TestHarness
from models_t import user_t
from xplore.database.models import AccessToken
from xplore.database.errors import InvalidTokenError, NotExistentTokenError,\
    ExpiredTokenError


def test_token():
    user = user_t.test_user()
    token = AccessToken.create(user)
    return token

class AccessTokenTest(unittest.TestCase):
    """Test suite for the AccessToken model"""

    def setUp(self):
        self.testharness = TestHarness()
        self.testharness.setup()

    def tearDown(self):
        self.testharness.destroy()

    def test_create(self):
        """Simple test for creation of an AccessToken for an existing user"""
        test_user = user_t.test_user()
        token = AccessToken.create(test_user)
        self.assertEqual(len(AccessToken.get_all()), 1)
        self.assertEqual(token.associated_user, test_user.key)

    def test_invalidate(self):
        """Test for the invalidate_tokens method, it checks that the function
        correctly sets the valid flag to False in all tokens for a given user
        """
        test_user = user_t.test_user()
        token = AccessToken.create(test_user)
        AccessToken.invalidate_tokens(test_user)
        token_2 = AccessToken.create(test_user)
        self.assertEqual(len(AccessToken.get_all()), 2)
        self.assertFalse(AccessToken.get_by_id(token.key.id()).valid)
        self.assertTrue(AccessToken.get_by_id(token_2.key.id()).valid)
        AccessToken.invalidate_tokens(test_user)
        self.assertFalse(any(t.valid for t in AccessToken.get_all()))

    def test_validate(self):
        """Check the validation method for tokens. It verifies that the token
        is accepted only when it exists in the datastore, it is marked as valid
        and the expiration time is after the current time
        """
        test_user = user_t.test_user()
        self.assertRaises(NotExistentTokenError, AccessToken.validate_token,
                          'atoken')
        token = AccessToken.create(test_user)
        self.assertEqual(AccessToken.validate_token(token.token_string),
                         test_user.key)
        AccessToken.invalidate_tokens(test_user)
        token_2 = AccessToken.create(test_user)
        self.assertRaises(InvalidTokenError,
                          AccessToken.validate_token,
                          token.token_string)
        self.assertEqual(AccessToken.validate_token(token_2.token_string),
                         test_user.key)
        AccessToken._ACCESS_TOKEN_EXPIRATION_TIME = 2
        self.assertEqual(AccessToken.validate_token(token_2.token_string),
                         test_user.key)
        token_3 = AccessToken.create(test_user)
        self.assertEqual(AccessToken.validate_token(token_3.token_string),
                         test_user.key)
        time.sleep(2)
        self.assertRaises(ExpiredTokenError,
                          AccessToken.validate_token,
                          token_3.token_string)

if __name__ == "__main__":
    unittest.main()
