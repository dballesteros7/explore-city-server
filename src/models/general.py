'''
Module that defines a general model for the server from which all others model
inherit.
Created on Jan 10, 2014

@author: diegob
'''
from google.appengine.ext import ndb


class GenericModel(ndb.Model):
    '''
    Generic model class for the server's data schema. It defines
    attributes of common use.
    '''

    ##############
    # Constants  #
    ##############
    MAX_QUERY_RESULTS = int(1e6)

    ##############
    # Queries    #
    ##############

    @classmethod
    def query_by_id(cls, objectId, ancestor = None):
        '''
        Query for a single object given its id, if it exists. Otherwise
        returns an empty list.
        '''
        if ancestor is not None:
            result = cls.get_by_id(objectId, parent = ancestor)
        else:
            result = cls.get_by_id(objectId)
        if result is not None:
            return [result]
        return []

    @classmethod
    def query_all(cls, max_results, ancestor = None):
        '''
        Query for all objects of this kind. Restrict the number of results
        to the given limit. None indicates return all results.
        '''
        if max_results is None:
            max_results = cls.MAX_QUERY_RESULTS
        if ancestor is not None:
            qry = cls.query(ancestor = ancestor)
        else:
            qry = cls.query()
        results = qry.fetch(max_results)
        return results
