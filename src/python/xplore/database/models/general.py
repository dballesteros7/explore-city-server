from google.appengine.ext import ndb

__all__ = ['GenericModel']


class GenericModel(ndb.Model):
    """Based model for the system.

    This defines basic shared attributes and methods for all models in the
    system.

    Class attributes:
        _MAX_QUERY_RESULTS: Default maximum number of results to return in a
            query.
    """
    _MAX_QUERY_RESULTS = int(1e6)

    @classmethod
    def default_ancestor(cls):
        """Return the default ancestor for the model class.

        This must be overriden by subclass models which desire a non-None
        ancestor key.
        """
        return None

    @classmethod
    def create_with_default_ancestor(cls, **kwargs):
        """Call the constructor for the model with the default ancestor key as
        parent.

        Arguments:
            kwargs: Arguments required for the model creation.

        Returns:
            The newly created model class. Note that the model is not yet
            stored in the datastore.
        """
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
                        ancestor=cls.default_ancestor())
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
