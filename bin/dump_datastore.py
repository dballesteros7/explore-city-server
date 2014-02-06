'''
Utility script to dump all missions and waypoints from the datastore into a
json file with a reasonably stable format for resubmission to other instance
of the server.
Created on Feb 5, 2014

@author: diegob
'''

import json
import os.path
import requests
import sys


def save_images(waypoints, image_dir):
    for waypoint in waypoints['waypoints']:
        image = waypoint['image_url']
        response_1 = requests.get(image, stream = True)
        response_1.raise_for_status()
        file_path = os.path.join(image_dir, image.split('/')[-1] + '.jpeg')
        with open(file_path, 'wb') as f:
            for chunk in response_1.iter_content():
                f.write(chunk)
        waypoint['image_url'] = file_path

def get_waypoints(base_host, output_file, image_dir):
    url_server = '%s/waypoints' % base_host
    response_1 = requests.get(url_server)
    response_1.raise_for_status()
    data = response_1.json()
    save_images(data, image_dir)
    json.dump(data, output_file)

def get_missions(base_host, output_file):
    url_server = '%s/missions' % base_host
    response_1 = requests.get(url_server)
    response_1.raise_for_status()
    data = response_1.json()
    json.dump(data, output_file)

def main():
    data_dir = os.path.join(os.path.dirname(__file__), '../data')
    waypoint_file = open(os.path.join(data_dir, 'waypoints.json'), 'w')
    mission_file = open(os.path.join(data_dir, 'missions.json'), 'w')
    get_waypoints('http://dev.street-view-density.appspot.com/api', waypoint_file, data_dir)
    get_missions('http://dev.street-view-density.appspot.com/api', mission_file)
    waypoint_file.close()
    mission_file.close()

if __name__ == '__main__':
    sys.exit(main())