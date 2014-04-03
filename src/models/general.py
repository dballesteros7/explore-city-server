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
    def default_ancestor(cls):
        '''
        Provides a default ancestor for the model. This must be overriden
        by each individual model if they desire ancestor queries by default.
        '''
        return None

    @classmethod
    def query_by_id(cls, objectId, ancestor = None):
        '''
        Query for a single object given its id, if it exists. Otherwise
        returns an empty list.
        '''
        if ancestor is None:
            ancestor = cls.default_ancestor()
        result = cls.get_by_id(objectId, parent = ancestor)
        if result is not None:
            return [result]
        return []

    @classmethod
    def get_by_urlsafe(cls, urlsafe):
        '''
        Query for a single object given its key in urlsafe format.
        '''
        keyobject = ndb.Key(urlsafe = urlsafe)
        model_instance = keyobject.get()
        return model_instance

    @classmethod
    def query_all(cls, max_results = None, ancestor = None):
        '''
        Query for all objects of this kind. Restrict the number of results
        to the given limit. None indicates return all results.
        '''
        # If no ancestor was given, try with the default one
        if ancestor is None:
            ancestor = cls.default_ancestor()
        if max_results is None:
            max_results = cls.MAX_QUERY_RESULTS
        qry = cls.query(ancestor = ancestor)
        results = qry.fetch(max_results)
        return results
