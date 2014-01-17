'''
CLI module that provides functionality for admins to upload and query waypoints
and missions. And any other useful thing that may come along the way.

Created on Jan 13, 2014

@author: diegob
'''
import argparse
import json
import sys

import requests


def create_waypoint(latitude, longitude, name, image_path, base_host):
    # Make sure that the file exist before doing anything
    files = {'image' : open(image_path, 'rb')}

    # Get the URL for uploading the image
    url_server = '%s/upload' % base_host
    response_1 = requests.get(url_server)
    response_1.raise_for_status()
    data = response_1.json()

    # Upload the image to the given url and retrieve the key
    response_2 = requests.post(data['upload_url'], files = files)
    response_2.raise_for_status()
    image_data = response_2.json()

    # Upload the metadata with the image key
    headers = {'content-type' : 'application/json'}
    dataObject = {'latitude' : latitude,
                  'longitude' : longitude,
                  'name' : name,
                  'image_key' : image_data['image_key']}
    url_waypoint = '%s/waypoints' % base_host
    response_3 = requests.post(url_waypoint, data = json.dumps(dataObject), headers = headers)
    response_3.raise_for_status()
    return

def create_mission(name, waypoint_names, base_host):
    # POST the required data, nothing fancy
    url_mission = '%s/missions' % base_host
    headers = {'content-type' : 'application/json'}
    dataObject = {'name' : name,
                  'waypoints' : waypoint_names}
    response = requests.post(url_mission, data = json.dumps(dataObject), headers = headers)
    response.raise_for_status()
    return

def check_location_tuple(arg):
    value = tuple(float(x) for x in arg.split(','))
    return value

def build_options():
    option_parser = argparse.ArgumentParser(description = 'CLI for admins of the explore-city server.')

    # Add the option for the base URL
    option_parser.add_argument('--url', default = 'http://dev.street-view-density.appspot.com/api')

    # Add the option either create a mission or a waypoint
    option_parser.add_argument('action', choices = ['m', 'w'])

    # Add the options for waypoints
    option_parser.add_argument('--location', type = check_location_tuple, nargs = '+', metavar = 'LAT,LON')
    option_parser.add_argument('--image-path', nargs = '+')

    # Add the name option
    option_parser.add_argument('--name', nargs = '+')
    return option_parser

def main():
    option_parser = build_options()
    options = option_parser.parse_args()
    if options.action == 'w':
        if options.location is None or options.image_path is None:
            raise Exception("No location or image paths provided")
        if len(options.location) != len(options.image_path):
            raise Exception("Number of locations and images doesn't match")
        if len(options.location) != len(options.name):
            raise Exception("Number of locations and names doesn't match")
        for location, path, name in zip(options.location, options.image_path, options.name):
            create_waypoint(location[0], location[1], name, path, options.url)

    if options.action == 'm':
        if len(options.name) <= 1:
            raise Exception("At least a valid waypoint name must be specified.")
        else:
            if options.location is not None and options.image_path is not None:
                if len(options.location) != len(options.image_path):
                    raise Exception("Number of locations and images doesn't match")
                if len(options.location) != len(options.name) - 1:
                    raise Exception("Number of locations and names doesn't match")
                for location, path, name in zip(options.location, options.image_path, options.name[1:]):
                    create_waypoint(location[0], location[1], name, path, options.url)
            create_mission(options.name[0], options.name[1:], options.url)

if __name__ == '__main__':
    sys.exit(main())
