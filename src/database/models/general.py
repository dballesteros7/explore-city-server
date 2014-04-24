from google.appengine.ext import ndb


__all__ = ['GenericModel']

class GenericModel(ndb.Model):

    _MAX_QUERY_RESULTS = int(1e6)

    @classmethod
    def default_ancestor(cls):
        return None

    @classmethod
    def create_with_default_ancestor(cls, **kwargs):
        return cls(parent=cls.default_ancestor(),
                  **kwargs)

    @classmethod
    def get_by_id(cls, entity_id, ancestor=None):
        if ancestor is None:
            ancestor = cls.default_ancestor()
        result = super(GenericModel, cls).get_by_id(entity_id,
                                                     parent=ancestor)
        return result

    @classmethod
    def get_by_urlsafe(cls, urlsafe):
        keyobject = ndb.Key(urlsafe=urlsafe)
        model_instance = keyobject.get()
        return model_instance
    
    @classmethod
    def get_by_property(cls, prop, value):
        qry = cls.query(getattr(cls, prop) == value,
                        ancestor = cls.default_ancestor())
        results = qry.fetch()
        return results

    @classmethod
    def get_all(cls, max_results=None, ancestor=None):
        if ancestor is None:
            ancestor = cls.default_ancestor()
        if max_results is None:
            max_results = cls._MAX_QUERY_RESULTS
        qry = cls.query(ancestor=ancestor)
        results = qry.fetch(max_results)
        return results

    @classmethod
    def delete(cls):
        cls.key.delete()
