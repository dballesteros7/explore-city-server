import webapp2
from webapp2_extras.routes import RedirectRoute

from handler.api.auth import TokenResource
from handler.api.imageservice import ImageUploadHandler, ImageUploadUrlProvider
from handler.api.missions import MissionResource
from handler.api.submissions import SubmissionResource
from handler.api.users import UserResource
from handler.api.waypoints import WaypointResource
from handler.pages.admin import AdminPage
import secrets

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': secrets.session_cookie_key,
    'cookie_args' : {  # 'secure' : True,
                     # 'httponly' : True
                     }
}
config['webapp2_extras.jinja2'] = {
                                   'template_path' : 'html/templates'}

app = webapp2.WSGIApplication([
  # API routes
  RedirectRoute(r'/api/upload', handler = ImageUploadHandler, methods = ['POST'], name = 'image-upload', strict_slash = True),
  RedirectRoute(r'/api/upload', handler = ImageUploadUrlProvider, methods = ['GET'], name = 'image-upload-url', strict_slash = True),
  RedirectRoute(r'/api/waypoints', handler = WaypointResource, name = 'waypoints-resource', strict_slash = True),
  RedirectRoute(r'/api/waypoints/<name>', handler = WaypointResource, name = 'waypoints-resource-named', strict_slash = True),
  RedirectRoute(r'/api/missions', handler = MissionResource, name = 'missions-resource', strict_slash = True),
  RedirectRoute(r'/api/missions/<name>', handler = MissionResource, name = 'missions-resource-named', strict_slash = True),
  RedirectRoute(r'/api/submissions', handler = SubmissionResource, name = 'submissions-resource', strict_slash = True),
  RedirectRoute(r'/api/submissions/<name>', handler = SubmissionResource, name = 'submissions-resource-named', strict_slash = True),
  RedirectRoute(r'/api/users', handler = UserResource, name = 'users-resource', strict_slash = True),
  RedirectRoute(r'/api/users/<userkey>', handler = UserResource, name = 'users-resource-named', strict_slash = True),
  # Auth API
  RedirectRoute(r'/auth/token', handler = TokenResource, name = 'auth-token-provider', methods = ['GET'], strict_slash = True),
  # HTML pages
  RedirectRoute(r'/admin', handler = AdminPage, name = 'admin-page', methods = ['GET'], strict_slash = True),
], config = config)
