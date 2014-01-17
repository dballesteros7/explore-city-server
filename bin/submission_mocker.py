'''
CLI module that mocks an app submission for testing.
Created on Jan 17, 2014

@author: diegob
'''

import argparse
import json
import sys

import requests


def post_submission(mission, waypoint, image_path, base_host):
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
    data_object = {'mission' : mission,
                   'waypoint' : waypoint,
                   'image_key' : image_data['image_key']}
    url_waypoint = '%s/submissions' % base_host
    response_3 = requests.post(url_waypoint, data = json.dumps(data_object), headers = headers)
    response_3.raise_for_status()
    return

def build_options():
    option_parser = argparse.ArgumentParser(description = 'Mocker CLI for submissions.')

    # Add the option for the base URL
    option_parser.add_argument('--url', default = 'http://dev.street-view-density.appspot.com/api')

    # Add the argument for image data
    option_parser.add_argument('image')

    # Add the arguments for mission and waypoint
    option_parser.add_argument('mission')
    option_parser.add_argument('waypoint')

    return option_parser

def main():
    option_parser = build_options()
    options = option_parser.parse_args()
    post_submission(options.mission, options.waypoint,
                    options.image, options.url)

if __name__ == '__main__':
    sys.exit(main())
