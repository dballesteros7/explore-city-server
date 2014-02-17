'''
Utility script to restore a datastore instance from json files and images
created from the dump_datastore script.
Created on Feb 6, 2014

@author: diegob
'''
import json
import os.path
import sys

from admin_utils import create_waypoint, create_mission


def upload_waypoints(waypoint_json, base_host):
    waypoints = json.load(waypoint_json)
    for waypoint in waypoints['waypoints']:
        create_waypoint(waypoint['name'], waypoint['latitude'], waypoint['longitude'], waypoint['image_url'], base_host)

def upload_missions(mission_json, base_host):
    missions = json.load(mission_json)
    for mission in missions['missions']:
        create_mission(mission['name'], [x['name'] for x in mission['waypoints']], base_host)

def main():
    data_dir = os.path.join(os.path.dirname(__file__), '../data/')
    waypoint_json_f = open(os.path.join(data_dir, 'waypoints.json'))
    upload_waypoints(waypoint_json_f, 'http://dev.street-view-density.appspot.com/api')
    waypoint_json_f.close()
    mission_json_f = open(os.path.join(data_dir, 'missions.json'))
    upload_missions(mission_json_f, 'http://dev.street-view-density.appspot.com/api')
    mission_json_f.close()

if __name__ == '__main__':
    sys.exit(main())