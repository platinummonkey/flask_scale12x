from tools.bulbs_wrapper import Node
from bulbs.property import String, Integer
from flask.ext.testing import TestCase
from nose.plugins.attrib import attr
import factory
from tools.ogm_factory import BulbsWrapperModelFactory
import logging

logger = logging.getLogger(__name__)


class NonPerson(Node):
    element_type = 'nonperson'

    name = String(nullable=False)
    age = Integer()

    some_random_attribute = 4

    @classmethod
    def some_classmethod_fcn(cls):
        return cls.element_type

    @staticmethod
    def some_staticmethod_fcn(x):
        return x

    def some_instance_fcn(self):
        return self.age

    @property
    def some_property(self):
        return self.age

    def __repr__(self):
        return u'%s(name=%s, age=%s)' % (self.__class__.__name__, self.name, self.age)


class NonPersonFactory(BulbsWrapperModelFactory):
    FACTORY_FOR = NonPerson

    name = factory.Sequence(lambda n: 'Some Guy {0}'.format(n))
    age = factory.Sequence(lambda n: n+10)


@attr('env_test', 'bulbs_wrapper', 'bulbs_wrapper_factory')
class BulbsFactoryWrapperTestCase(TestCase):
    """ Test the BulbsWrapperModelFactory subclass of factory_boy.Factory for our OGM for Titan """

    def create_app(self):
        from app import app
        return app

    def setUp(self):
        self.klass = NonPerson
        self.klass._setup_klass_(self.app)
        self.factory = NonPersonFactory

    def tearDown(self):
        element_proxy = NonPerson._GRAPH.nonperson
        try:  # try to cleanup from previous test
            nodes = element_proxy.get_all()
            for p in nodes:
                logger.debug("Got nonperson (%s): %s" % (p.eid, p))
                element_proxy.delete(p.eid)
                logger.debug("Deleted person")
        except Exception as e:
            logger.exception(e)

    def test_factory_functionality(self):
        """ Make sure the factory wrapper creates a new Person and returns it. There is no 'building', only creating.

        This is important for general usage syntax, as you would want a full OGM
        """
        element_class = self.klass._PROXY.element_class
        element_proxy = self.klass._GRAPH.nonperson
        try:  # try to cleanup from previous test
            #Person._GRAPH.clear()
            nodes = element_proxy.index.lookup(name='Some Guy 0')
            for p in nodes:
                logger.debug("Got nonperson (%s): %s" % (p.eid, p))
                element_proxy.delete(p.eid)
                logger.debug("Deleted person")
        except Exception as e:
            logger.exception(e)
        logger.debug(dir(element_class))

        # use the factory class to generate a Person (aka PersonModel)
        obj = self.factory()
        logger.debug("obtained object %s is of type: %s" % (obj, type(obj)))
        self.assertIsInstance(obj, element_class)

        # ensure that the values stuck
        self.assertEqual(obj.name, 'Some Guy 0')
        self.assertEqual(obj.age, 10)

        self.assertEqual(obj.some_staticmethod_fcn(1), 1)
        self.assertEqual(obj.some_instance_fcn(), 10)
        self.assertEqual(obj.some_property, 10)

        self.assertEqual(repr(obj), "NonPersonModel(name=Some Guy 0, age=10)")