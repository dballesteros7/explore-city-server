from google.appengine.api import users
import json
from datetime import date

from xplore.database.models import User, MissionProgress, MissionWaypoint
from xplore.handler.api.base_service import BaseResource


class StatisticsResource(BaseResource):
    def waypoint_info_for_user(self, name):
        gae_user = users.get_current_user()
        current_user = User.get_by_google_id(gae_user.user_id())
        waypoint = MissionWaypoint.get_by_property('name', name)[0]
        if current_user is None:
            self.abort(400)
        statistics = MissionProgress.statistics_for_user_and_waypoint(
                                                               current_user.key,
                                                               waypoint.key)
        parsed_statistics = [s.to_json() for s in statistics]
        self.build_base_response()
        self.response.out.write(json.dumps(parsed_statistics))

    def waypoint_popularity(self, name):
        waypoint = MissionWaypoint.get_by_property('name', name)[0]
        statistics = MissionProgress.visits_for_waypoint(waypoint.key)
        visits_by_date = {}
        for stat in statistics:
            if stat.timestamp.date() not in visits_by_date:
                visits_by_date[stat.timestamp.date()] = 0
            visits_by_date[stat.timestamp.date()] += 1
        if date.today() not in visits_by_date:
            visits_by_date[date.today()] = 0
        if waypoint.created_on not in visits_by_date:
            visits_by_date[waypoint.created_on] = 0
        results = []
        for visit_date in sorted(visits_by_date.keys()):
            results.append({'datetime' : visit_date.isoformat(),
                            'visits' : visits_by_date[visit_date]})
        self.build_base_response()
        self.response.out.write(json.dumps(results))