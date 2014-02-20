from tools.bulbs_wrapper import Node, Relationship
from bulbs.titan import Graph as BulbsGraph
from bulbs.model import Node as BulbsNode, Relationship as BulbsRelationship
from bulbs.model import NodeProxy as BulbsNodeProxy, RelationshipProxy as BulbsRelationshipProxy
from bulbs.property import String, Integer
from flask.ext.testing import TestCase
from nose.plugins.attrib import attr
from types import GeneratorType
import logging

logger = logging.getLogger(__name__)


class Person(Node):
    element_type = 'person'
    _SCRIPTS = ['modeltest']

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


class Knows(Relationship):

    label = 'knows'

    description = String()


@attr('env_test', 'bulbs_wrapper')
class BulbsWrapperTestCase(TestCase):
    """ Test the BulbsWrapper OGM for Titan """

    def create_app(self):
        from app import app
        return app

    def setUp(self):
        self.klass = Person
        self.edge_klass = Knows
        self.klass._setup_klass_(self.app)
        self.edge_klass._setup_klass_(self.app)
        self.proxy_attributes = ['__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__',
                                 '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__',
                                 '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__',
                                 'create', 'delete', 'get', 'get_all', 'get_property_keys', 'remove_properties',
                                 'update']

    def tearDown(self):
        element_proxy = Person._GRAPH.person
        edge_element_proxy = Knows._GRAPH.knows
        # try to cleanup from previous test
        try:
            nodes = element_proxy.get_all()  # .index.lookup(name='test')
            for p in nodes:
                logger.debug("Got person (%s): %s" % (p.eid, p))
                element_proxy.delete(p.eid)
                logger.debug("Deleted person")
        except Exception as e:
            logger.exception(e)
        try:
            relations = edge_element_proxy.get_all()
            for r in relations:
                logger.debug("Got edge (%s): %s" % (r.eid, r))
                edge_element_proxy.delete(r.eid)
                logger.debug("Deleted edge")
        except Exception as e:
            logger.exception(e)

    def test_klass_has_proxy_attributes(self):
        """ Make sure the attributes exist and are not None for a Node"""
        # check existence
        self.assertTrue(hasattr(self.klass, '_GRAPH'))
        self.assertTrue(hasattr(self.klass, '_PROXY'))
        self.assertTrue(hasattr(self.klass, '_SCRIPTS'))
        self.assertTrue(hasattr(self.klass, 'PersonModel'))
        # check that they are not None
        self.assertIsNotNone(self.klass._GRAPH)
        self.assertIsNotNone(self.klass._PROXY)
        self.assertIsNotNone(self.klass.PersonModel)
        # check that they have the right type
        self.assertIsInstance(self.klass._GRAPH, BulbsGraph)
        self.assertIsInstance(self.klass._PROXY, BulbsNodeProxy)

    def test_edge_klass_has_proxy_attributes(self):
        """ Make sure the attributes exist and are not None for a Relationship"""
        # check existence
        self.assertTrue(hasattr(self.edge_klass, '_GRAPH'))
        self.assertTrue(hasattr(self.edge_klass, '_PROXY'))
        self.assertTrue(hasattr(self.edge_klass, '_SCRIPTS'))
        self.assertTrue(hasattr(self.edge_klass, 'KnowsModel'))
        # check that they are not None
        self.assertIsNotNone(self.edge_klass._GRAPH)
        self.assertIsNotNone(self.edge_klass._PROXY)
        self.assertIsNotNone(self.edge_klass.KnowsModel)
        # check that they have the right type
        self.assertIsInstance(self.edge_klass._GRAPH, BulbsGraph)
        self.assertIsInstance(self.edge_klass._PROXY, BulbsRelationshipProxy)

    def test_class_has_proxy_proxy_attributes(self):
        """ Make sure that the underlying bulbs Proxy methods have been proxied upstream to the current klass """

        self.assertEqual(Person.__name__, 'Person')
        self.assertTrue(issubclass(Person._NODE_KLASS, BulbsNode))
        self.assertIsInstance(Person._PROXY, BulbsNodeProxy)
        for attr in self.proxy_attributes:
            self.assertIn(attr, dir(Person))

        # relationship
        self.assertEqual(Knows.__name__, 'Knows')
        self.assertTrue(issubclass(Knows._NODE_KLASS, BulbsRelationship))
        self.assertIsInstance(Knows._PROXY, BulbsRelationshipProxy)
        for attr in self.proxy_attributes:
            self.assertIn(attr, dir(Knows))

    def test_class_through_proxy_has_method_fcns(self):
        """ Make sure that static, class and instance methods pass through the bulbs Proxy class fine to the
        element_class.

        This is important for general usage syntax, as you would want a full OGM
        """
        element_class = Person._PROXY.element_class
        element_proxy = Person._GRAPH.person
        logger.debug(dir(element_class))

        # first make sure all callable(s)/property are available
        self.assertTrue(hasattr(element_class, 'some_classmethod_fcn'))
        self.assertTrue(hasattr(element_class, 'some_staticmethod_fcn'))
        self.assertTrue(hasattr(element_class, 'some_instance_fcn'))
        self.assertTrue(hasattr(element_class, 'some_property'))
        self.assertTrue(hasattr(element_class, 'some_random_attribute'))

        # check their values
        self.assertEqual(element_class.some_random_attribute, 4)
        self.assertEqual(element_class.some_classmethod_fcn(), 'person')
        obj = element_proxy.create(name='test', age=2)
        logger.debug("obtained object %s is of type: %s" % (obj, type(obj)))
        self.assertIsInstance(obj, element_class)

        self.assertEqual(obj.some_staticmethod_fcn(1), 1)
        self.assertEqual(obj.some_instance_fcn(), 2)
        self.assertEqual(obj.some_property, 2)

        self.assertEqual(repr(obj), "PersonModel(name=test, age=2)")

    def test_wrapper_class_has_groovy_classmethods(self):
        """ Make sure private groovy methods are applied as classmethods to the wrapper class.

        These custom groovy functions are useful for optimized common queries that can be performed on the database
        side.
        """
        # first create a person
        element_proxy = Person._GRAPH.person
        obj = element_proxy.create(name='test', age=32)

        # check method exists
        self.assertTrue(hasattr(Person, 'get_older_30'))
        self.assertEqual(Person.__dict__['get_older_30'].__class__.__name__, 'classmethod')

        # use method and check return
        vertices = Person.get_older_30()  # we expect 1 person to exist
        self.assertIsInstance(vertices, GeneratorType)
        # we receive a generator, so we need to generate a list
        vertex_list = [vertex for vertex in vertices]
        self.assertEqual(len(vertex_list), 1)
        self.assertEqual(obj, vertex_list[0])

    def test_relationship_query_returns_object_instance(self):
        """ Make sure when we query a Relationship model instance's outV or inV we get back a instantiated Node model

        This is critical for the OGM to really be an OGM, otherwise we are guessing like idiots as to what the Vertex is
        supposed to represent.
        """
        # first create a people
        element_proxy = Person._GRAPH.person
        bob = element_proxy.create(name='bob', age=32)
        alice = element_proxy.create(name='alice', age=30)

        # create the relationship
        edge_element_proxy = Knows._PROXY  # Knows._GRAPH.knows
        friends = edge_element_proxy.create(bob, alice, description='great friends')

        self.assertEqual(friends.outV(), bob)
        self.assertEqual(friends.inV(), alice)

        # okay let's query and try it again
        friend = Knows.all(bob).next()

        # let's ensure that it is the same relationship
        self.assertEqual(friend, friends)
        self.assertEqual(friend.outV(), bob)
        self.assertEqual(friend.inV(), alice)