import os.path
import sys

from admin_utils import create_waypoint_with_url


BASE_HOST = 'http://localhost:8080/api'


def main():

    with open(
        os.path.join(
            os.path.dirname(__file__), '../data/valid_images.csv'),
            'r') as waypoints_file:
        for line in waypoints_file:
            tokens = line.strip().split(',')
            system_id = tokens[0]
            #flickr_id = tokens[1]
            latitude = float(tokens[2])
            longitude = float(tokens[3])
            image_url = tokens[4]

            create_waypoint_with_url(
                'Waypoint %s' % (system_id),
                latitude, longitude, image_url, BASE_HOST)

if __name__ == '__main__':
    sys.exit(main())
