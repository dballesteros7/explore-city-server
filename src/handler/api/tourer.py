from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import json
from os.path import os
import urllib

from handler.api.base_service import BaseResource
from models.general import GenericModel
import root
import secrets
from utils.orienteering import Place, Solver


_CENTER_FOR_RADAR_SEARCH = '47.368620,8.539891'  # Zurich center (Hauptbahnhof)
_CITY_RADIUS = 1000  # 5km should cover most of Zurich

class Query(GenericModel):
    places = ndb.JsonProperty(required = True)

class TourerHandler(BaseResource):
    def format_place(self, place):
        place['latitude'] = place['geometry']['location']['lat']
        place['longitude'] = place['geometry']['location']['lng']
        return place

    def retrieve_places_for_types(self):
        requested_types = json.loads(self.request.params.get('types'))
        types_string = '|'.join(requested_types)
        base_url = 'https://maps.googleapis.com/maps/api/place/radarsearch/json'
        payload = {'key' : secrets.GOOGLE_APP_SERVER_KEY,
                   'location' : _CENTER_FOR_RADAR_SEARCH,
                   'radius' : _CITY_RADIUS,
                   'sensor' : 'false',
                   'types' : types_string}
        payload_serialized = urllib.urlencode(payload)
        response = urlfetch.fetch('%s?%s' % (base_url, payload_serialized))
        places_response = json.loads(response.content)
        formatted_places = [self.format_place(place) for place in places_response['results'][:10]]
        new_query = Query(places = formatted_places)
        new_query.put()
        self.build_base_response()
        self.response.out.write(json.dumps({'query_id' : new_query.key.urlsafe(),
                                            'places' : formatted_places}))

    def retrieve_types(self):
        types = []
        with open(os.path.join(root.APPLICATION_ROOT, 'places_types'), 'r') as f:
            for line in f:
                types.append(line.strip())
        self.build_base_response()
        self.response.out.write(json.dumps(types))

    def crazy(self):
        query_id = self.request.params.get('query_id')
        query = Query.get_by_urlsafe(query_id)
        real_places = []
        for place in query.places:
            place["value"] = 1
            real_places.append(Place(place))
        solver = Solver(real_places)
        print solver.rg_pq(real_places[0], real_places[0], 10, set(), 4)