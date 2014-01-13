'''
Created on Dec 10, 2013

@author: diegob
'''

import webapp2

from webapp2_extras.routes import RedirectRoute

from handler.api.imageservice import ImageUploadHandler, ImageUploadUrlProvider
from handler.api.waypoints import WaypointResource
from handler.api.missions import MissionResource


app = webapp2.WSGIApplication([
  RedirectRoute(r'/api/upload', handler = ImageUploadHandler, methods = ['POST'], name = 'image-upload', strict_slash = True),
  RedirectRoute(r'/api/upload', handler = ImageUploadUrlProvider, methods = ['GET'], name = 'image-upload-url', strict_slash = True),
  RedirectRoute(r'/api/waypoints', handler = WaypointResource, name = 'waypoints-resource', strict_slash = True),
  RedirectRoute(r'/api/waypoints/<name>', handler = WaypointResource, name = 'waypoints-resource-named', strict_slash = True),
  RedirectRoute(r'/api/missions', handler = MissionResource, name = 'missions-resource', strict_slash = True),
  RedirectRoute(r'/api/missions/<name>', handler = MissionResource, name = 'missions-resource-named', strict_slash = True),
])
