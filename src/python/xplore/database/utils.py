from .models import Mission

__all__ = ['get_missions_for_waypoint']

def get_missions_for_waypoint(waypoint_key):
    container_missions = Mission.query_by_waypoint(waypoint_key)
    return container_missions