from google.appengine.api import files
import unittest

from harness import TestHarnessWithWeb


def create_blob(contents, mime_type):
    fn = files.blobstore.create(mime_type=mime_type)
    with files.open(fn, 'a') as f:
        f.write(contents)
    files.finalize(fn)
    return files.blobstore.get_blob_key(fn)


class TestWaypointResource(unittest.TestCase):

    def setUp(self):
        self.testharness = TestHarnessWithWeb()
        self.testharness.setup()

    def tearDown(self):
        self.testharness.destroy()

    def test_crud(self):
        """Test the api/waypoints endpoint for basic CRUD operations.

        First it tests the creation of a waypoint with an image_key from the
        test blobstore, then it checks that the waypoint can be retrieved back
        given its name and then updated using the PUT verb. Finally it deletes
        the waypoint using the DELETE verb.
        """
        params = {'name': 'TestWaypoint',
                  'latitude': 24.38,
                  'longitude': -133.23213,
                  'image_key': create_blob('Really cool image',
                                           'application/octet-stream')}
        resp = self.testharness.testapp.post('/api/waypoints',
                                             params)
        self.assertEqual(resp.status_int, 201)
        self.assertEqual(resp.json['name'], params['name'])
        resp2 = self.testharness.testapp.get(resp.json['content_url'])
        self.assertEqual(resp2.status_int, 200)
        waypoints = resp2.json['waypoints']
        self.assertEqual(len(waypoints), 1)
        waypoint = waypoints[0]
        self.assertEqual(waypoint['name'], params['name'])
        self.assertEqual(waypoint['latitude'], params['latitude'])
        self.assertEqual(waypoint['longitude'], params['longitude'])
        params['longitude'] = 133.23213
        resp3 = self.testharness.testapp.put(resp.json['content_url'],
                                             params)
        self.assertEqual(resp3.status_int, 200)
        resp4 = self.testharness.testapp.get(resp.json['content_url'])
        self.assertEqual(resp4.status_int, 200)
        waypoints = resp4.json['waypoints']
        self.assertEqual(len(waypoints), 1)
        waypoint = waypoints[0]
        self.assertEqual(waypoint['name'], params['name'])
        self.assertEqual(waypoint['latitude'], params['latitude'])
        self.assertEqual(waypoint['longitude'], params['longitude'])
        self.assertEqual(waypoint['image_url'],
                         resp2.json['waypoints'][0]['image_url'])
        resp5 = self.testharness.testapp.delete(resp.json['content_url'])
        self.assertEqual(resp5.status_int, 200)
        resp6 = self.testharness.testapp.get(resp.json['content_url'])
        self.assertEqual(resp6.status_int, 200)
        self.assertEqual(len(resp6.json['waypoints']), 0)

    def test_crud_flickr_image(self):
        """Check that waypoints can be created and retrieved when created with
        an image URL instead of a blobstore key.
        """
        params = {'name': 'TestWaypoint',
                  'latitude': 24.38,
                  'longitude': -133.23213,
                  'image_url': 'http://example.com'}
        resp = self.testharness.testapp.post('/api/waypoints', params)
        self.assertEqual(resp.status_int, 201)
        self.assertEqual(resp.json['name'], params['name'])
        resp2 = self.testharness.testapp.get(resp.json['content_url'])
        self.assertEqual(resp2.status_int, 200)
        waypoints = resp2.json['waypoints']
        self.assertEqual(len(waypoints), 1)
        waypoint = waypoints[0]
        self.assertEqual(waypoint['name'], params['name'])
        self.assertEqual(waypoint['latitude'], params['latitude'])
        self.assertEqual(waypoint['longitude'], params['longitude'])
        self.assertEqual(waypoint['image_url'], params['image_url'])


if __name__ == "__main__":
    unittest.main()
