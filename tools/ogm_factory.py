from __future__ import unicode_literals
from factory import base
from factory.compat import is_string
from bulbs.model import RelationshipProxy
import factory as factory


class BulbsWrapperModelFactory(base.Factory):
    """Factory for Wrapped Bulbs models. """

    ABSTRACT_FACTORY = True

    _associated_model = None

    @classmethod
    def _load_target_class(cls):
        """ So we can support potential circular import problems, by using normal werkzueg.utils.import_string import
        specification.
        """
        associated_class = super(BulbsWrapperModelFactory, cls)._load_target_class()

        if is_string(associated_class) and '.' in associated_class:
            if cls._associated_model is None:
                from werkzeug.utils import import_string
                cls._associated_model = import_string(associated_class)
            return cls._associated_model

        return associated_class

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        """Create an instance of the model, and save it to the database."""
        if issubclass(target_class._PROXY.__class__, RelationshipProxy):
            """ @type target_class._PROXY: RelationshipProxy """
            assert ('outV' in kwargs and 'inV' in kwargs), "Relationships require in and out Vertices"
            obj = target_class._PROXY.create(outV=kwargs.get('outV'), inV=kwargs.get('inV'), *args, **kwargs)
        else:
            """ @type target_class._PROXY: NodeProxy """
            obj = target_class._PROXY.create(*args, **kwargs)
        return obj

__all__ = ['factory', 'BulbsWrapperModelFactory']