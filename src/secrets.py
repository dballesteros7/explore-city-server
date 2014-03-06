'''Module containing the secrets of the project. KEEP THIS FILE SECRET.
It must define the following values:

session_cookie_key : Key used for signing secure session cookies.

.. moduleauthor:: Diego Ballesteros <diegob@student.ethz.ch>
'''

session_cookie_key = "Il0v3c00ki3ss41dth3c00k13m0ns74"

# Google APIs
GOOGLE_APP_ID = '528090180269-rj0gvnu2toemhtee60nks0i45cgkodb8.apps.googleusercontent.com'
GOOGLE_APP_SECRET = 'iIRyGNuR1ZyXnCzv82XOTOg4'

# Facebook auth apis
FACEBOOK_APP_ID = '1376253562646544'
FACEBOOK_APP_SECRET = '23418f98fc9df1a1509cc9d955732da7'

# Key/secret for both LinkedIn OAuth 1.0a and OAuth 2.0
# https://www.linkedin.com/secure/developer
LINKEDIN_KEY = '7780xiacv66jv3'
LINKEDIN_SECRET = 'Irjvwm17n8ZjcAN8'

# https://manage.dev.live.com/AddApplication.aspx
# https://manage.dev.live.com/Applications/Index
WL_CLIENT_ID = 'client id'
WL_CLIENT_SECRET = 'client secret'

# https://dev.twitter.com/apps
TWITTER_CONSUMER_KEY = 'oauth1.0a consumer key'
TWITTER_CONSUMER_SECRET = 'oauth1.0a consumer secret'

# https://foursquare.com/developers/apps
FOURSQUARE_CLIENT_ID = 'client id'
FOURSQUARE_CLIENT_SECRET = 'client secret'

# config that summarizes the above
AUTH_CONFIG = {
  # OAuth 2.0 providers
  'google'      : (GOOGLE_APP_ID, GOOGLE_APP_SECRET,
                  'https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email'),
  'linkedin2'   : (LINKEDIN_KEY, LINKEDIN_SECRET,
                  'r_basicprofile r_emailaddress'),
  'facebook'    : (FACEBOOK_APP_ID, FACEBOOK_APP_SECRET,
                  'user_about_me email'),
  'windows_live': (WL_CLIENT_ID, WL_CLIENT_SECRET,
                  'wl.signin'),
  'foursquare'  : (FOURSQUARE_CLIENT_ID,FOURSQUARE_CLIENT_SECRET,
                  'authorization_code'),

  # OAuth 1.0 providers don't have scopes
  'twitter'     : (TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET),
  'linkedin'    : (LINKEDIN_KEY, LINKEDIN_SECRET),

  # OpenID doesn't need any key/secret
}