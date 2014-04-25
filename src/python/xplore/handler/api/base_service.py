'''
Module that defines a base handler for all the API resources in the
server.
Created on Jan 16, 2014

@author: diegob
'''
import json
import webapp2

from xplore.handler.base import BaseHandler


class QueryType:
    '''
    Class that defines the types of queries that can be made to geolocated
    resources in the GET verb.
    '''
    ############################################################################
    # Constants
    ############################################################################

    DISTANCE_FROM_CENTER = 1
    BOUNDING_BOX = 2
    UNBOUNDED = 0

class BaseResource(BaseHandler):
    '''Base RequestHandler that serves as parent of all other handlers in the 
    API. It defines basic methods to deal with parameter validation, response
    building and request parsing.
    '''

    def parse_request_body(self, json_accepted = True,
                           urlencoded_accepted = True):
        '''
        Parse the request according to the accepted types, currently
        only supports two:
            - 'application/json'
            - 'application/x-www-form-urlencoded'
        It returns a dictionary-like object with the request parameters.
        Since this dictionary may come directly from the request then it is
        immutable.
        '''
        
        if not self.request.headers.get('Content_Type') and\
            not self.request.headers.get('Content-Type') :
            return self.request.params
        content_key = 'Content_Type'
        if not self.request.headers.get(content_key):
            content_key = 'Content-Type'
        if json_accepted and 'application/json' in self.request.headers.get(content_key):
            try:
                parameters = json.loads(self.request.body)
            except:
                # Assume bad JSON
                self.abort(400, detail = 'Bad JSON body.')
        elif urlencoded_accepted and \
            'application/x-www-form-urlencoded' in self.request.headers.get(content_key):
            parameters = self.request.params
        else:
            webapp2.abort(400, detail = 'Bad content type in header.')
        return parameters

    def build_base_response(self, status_code = 200):
        '''
        Build a basic response that is common to all API resources. The basic
        elements of this API are:
            - Content type is application/json
            - Encoding is UTF-8
        It also sets the status code to the given value.
        '''
        # All the API works on JSON responses
        self.response.headers['content-type'] = 'application/json'
        self.response.status = status_code
        return
