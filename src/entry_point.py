'''
Created on Dec 10, 2013

@author: diegob
'''

import webapp2

from handler.admin_interface import AdminUploadInterface, AdminUploader,\
    AdminWaypointRetrieval
from handler.client_interface import ClientWaypointProvider, \
    ClientMissionProvider
from handler.general_handler import ServeHandler


app = webapp2.WSGIApplication([
  ('/admin', AdminUploadInterface),
  ('/admin/upload', AdminUploader),
  ('/admin/get_mission', AdminWaypointRetrieval),
  ('/serve/([^/]+)?', ServeHandler),
  ('/get_waypoint', ClientWaypointProvider),
  ('/get_client', ClientMissionProvider)
])
