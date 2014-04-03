import unittest

from harness import TestHarness
from models.user import User, ExistingGoogleIdError, ExistingUsernameError, \
    ExistingEmailError


def test_user():
    mockup_auth_info = {'access_token':'1/fFAGRNJru1FTz70BzhT3Zg',
                            'refresh_token' : '2/fFAGRNJru1FTz80BzhT3Zg',
                            'expires_in':3920,
                            'token_type':'Bearer',
                            'user_gid' : '1234567890'}
    user_1_username = 'maleficent'
    user_1_email = 'maleficent@castle.com'
    return User.create(user_1_email, user_1_username, mockup_auth_info)

class UserTest(unittest.TestCase):

    def setUp(self):
        self.testharness = TestHarness()
        self.testharness.setup()

    def tearDown(self):
        self.testharness.destroy()

    def test_create(self):
        """Simple test for creation of a dummy user instance. It
        also checks several queries.
        """
        mockup_auth_info = {'access_token':'1/fFAGRNJru1FTz70BzhT3Zg',
                            'refresh_token' : '2/fFAGRNJru1FTz80BzhT3Zg',
                            'expires_in':3920,
                            'token_type':'Bearer',
                            'user_gid' : '1234567890'}
        mockup_auth_info_2 = {'access_token':'1/fFAGRNJru1FTz70BzhT3Zg',
                            'refresh_token' : '2/fFAGRNJru1FTz80BzhT3Zg',
                            'expires_in':3920,
                            'token_type':'Bearer',
                            'user_gid' : '1234567891'}
        user_1_username = 'maleficent'
        user_2_username = 'sleeping'
        user_1_email = 'maleficent@castle.com'
        user_2_email = 'sleeping@castle.com'

        user_1 = User.create(user_1_email, user_1_username, mockup_auth_info)
        self.assertEqual(user_1.key, User.get_by_email(user_1_email).key)
        self.assertEqual(user_1.key, User.get_by_username(user_1_username).key)
        self.assertEqual(user_1.key, User.get_by_google_id(mockup_auth_info['user_gid']).key)
        self.assertEqual(len(User.query_all()), 1)
        self.assertRaises(ExistingGoogleIdError, User.create, user_2_email, user_2_username, mockup_auth_info)
        self.assertRaises(ExistingUsernameError, User.create, user_2_email, user_1_username, mockup_auth_info_2)
        self.assertRaises(ExistingEmailError, User.create, user_1_email, user_2_username, mockup_auth_info_2)
        User.create(user_2_email, user_2_username, mockup_auth_info_2)
        self.assertEqual(len(User.query_all()), 2)
        return

if __name__ == "__main__":
    unittest.main()
