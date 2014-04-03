"""Script to retrieve relevant places of certain type in a reasonable radius,
then it uses the Flickr API to determine the "popularity" of each place and
with this it builds a graph which can be then run through a constrained-TSP
solver to get a "good route".
"""
import sys

import flickrapi
import requests
import networkx as nx
import matplotlib.pyplot as plt

# =============================================================================
# Google API key
# =============================================================================
google_api_key = "AIzaSyBJWijKmFSCDi9U5ZboNGIxqxZbTStqoPI"

# =============================================================================
# Flickr keys
# =============================================================================
flickr_api_key = '58552ea45d1c6fd1442ae64a6f1bcf15';
flickr_api_secret = '7b2a90eb77ac6541';

# =============================================================================
# "Constants"
# =============================================================================
_CENTER_FOR_RADAR_SEARCH = "47.368620,8.539891"  # Zurich center (Hauptbahnhof)
_CITY_RADIUS = 5000  # 5km should cover most of Zurich
_LOCATION_RADIUS = 0.2  # 200m around every location for the Flickr queries
_MIN_TAKEN_DATE = "2013-01-01 00:00:00"

class MyFlickr(object):
    def __init__(self):
        print "Initializing the Flickr API"
        print "==============================================================="
        self.flickr = flickrapi.FlickrAPI(flickr_api_key, flickr_api_secret);
        (token, frob) = self.flickr.get_token_part_one(perms = 'write');
        if not token:
            raw_input("Press ENTER after you authorized this program");
        self.flickr.get_token_part_two((token, frob));
        print "Flickr API ready"
        print "==============================================================="

    def retrieve_places_of_type(self, location_type = "museum"):
        print "Retrieving places of type %s" % location_type
        print "==============================================================="
        payload = {"key" : google_api_key,
                   "location" : _CENTER_FOR_RADAR_SEARCH,
                   "radius" : _CITY_RADIUS,
                   "sensor" : "false",
                   "types" : location_type}
        response = requests.get(url = "https://maps.googleapis.com/maps/api/place/radarsearch/json",
                     params = payload)
        formatted_results = response.json()
        print formatted_results
        if formatted_results["status"] != "OK":
            raise Exception("The radar search was not successful.\n%s" % formatted_results)
        print "Found %d places in the given area" % len(formatted_results["results"])
        print "==============================================================="
        return formatted_results["results"] #FIXME: For testing work with small sets

    def retrieve_near_pictures_for_place(self, lat, lng):
        res = self.flickr.photos_search(lon = lng, lat = lat,
                                   radius = _LOCATION_RADIUS,
                                   min_taken_date = _MIN_TAKEN_DATE)
        photos = res[0]
        number_of_photos = int(photos.attrib["total"])
        return number_of_photos

    def build_location_information(self):
        places = self.retrieve_places_of_type()
        for place in places:
            place["num_pics"] = self.retrieve_near_pictures_for_place(
                                        place["geometry"]["location"]["lat"],
                                        place["geometry"]["location"]["lng"])
            print place["num_pics"]
        return places

    def build_network(self):
        # Assume that places is less than 100 (otherwise the matrix API will blow up).
        places_with_pics = self.build_location_information()
        return
        origins = []
        for place in places_with_pics:
            origins.append("%s,%s" % (place["geometry"]["location"]["lat"],
                                    place["geometry"]["location"]["lng"]))
        payload = {"key" : google_api_key,
                   "mode" : "walking",
                   "origins" : "|".join(origins),
                   "destinations" : "|".join(origins),
                   "sensor" : "false"}
        response = requests.get(url = "https://maps.googleapis.com/maps/api/distancematrix/json",
                     params = payload)
        formatted_results = response.json()
        if formatted_results["status"] != "OK":
            raise Exception("The distance matrix call was not successful.\n%s" % formatted_results)
        place_network = nx.Graph()
        for idx, place in enumerate(places_with_pics):
            place_network.add_node(idx)
        for idx_row, row in enumerate(formatted_results["rows"]):
            for idx_column, element in enumerate(row["elements"]):
                if idx_row == idx_column:
                    continue
                duration = element["duration"]["value"]
                distance = element["distance"]["value"]
                place_network.add_edge(idx_row, idx_column,
                                       distance = distance,
                                       duration = duration)
        return place_network

def main():
    x = MyFlickr()
    x.build_network()

if __name__ == '__main__':
    sys.exit(main())
