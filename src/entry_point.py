import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'python/'))

import endpoints
from xplore.handler.api.waypoints import MissionWaypointApi
app = endpoints.api_server([MissionWaypointApi])
