'''
Module that defines a base handler for all the API resources in the
server.
Created on Jan 16, 2014

@author: diegob
'''
import json
import webapp2


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
