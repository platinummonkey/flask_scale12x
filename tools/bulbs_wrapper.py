from bulbs.model import Node as BulbsNode
from bulbs.model import Relationship as BulbsRelationship
import logging
import inspect
from os import path as ospath
from copy import copy
from types import GeneratorType

logger = logging.getLogger(__name__)


class BulbsWrapperMetaClass(type):

    def __getattr__(cls, item):
        try:
            v = getattr(cls._PROXY, item)
            return v
        except AttributeError as e:
            raise AttributeError(e)


class BulbsWrapper(object):

    __metaclass__ = BulbsWrapperMetaClass

    _NODE_KLASS = None
    _GRAPH = None
    _PROXY = None
    _WRAPPED_KLASS = None
    _SCRIPTS = []

    @classmethod
    def _setup_klass_(cls, app):
        cls._GRAPH = app.config['DATABASE']
        # first check to see if the proxy model already exists, if it does skip this step
        if not hasattr(cls._GRAPH, cls.__name__.lower()):
            ## create dynamic klass using the appropriate bulbs model
            # first get the properties and filter out our own wrapper properties
            our_klass_attributes = inspect.getmembers(cls, lambda a: not(inspect.isroutine(a)))
            our_klass_fcns = inspect.getmembers(cls, lambda a: inspect.isroutine(a))
            blacklist = ['__class__',  '__dict__', '__doc__', '__module__', '__weakref__', '_NODE_KLASS', '_GRAPH',
                         '_PROXY', '__new__', '__reduce__', '__reduce_ex__', '__format__', '__hash__', '__init__',
                         '__subclasshook__', '_setup_klass_', '_WRAPPED_KLASS', '__metaclass__', 'all', 'get', 'lookup',
                         'lookup_single', '_SCRIPTS']
            our_klass_attributes = [a for a in our_klass_attributes if not(a[0] in blacklist)]
            our_klass_fcns = [a for a in our_klass_fcns if not(a[0] in blacklist)]
            # dynamically create the new class and add the property to use it directly
            new_class = type(cls.__name__ + 'Model', (cls._NODE_KLASS,), dict(our_klass_attributes))
            # add in the methods
            for attr in our_klass_fcns:
                try:
                    fcn_type = type(cls.__dict__[attr[0]]).__name__
                    if fcn_type == 'staticmethod':
                        setattr(new_class, attr[0], staticmethod(attr[1]))
                    elif fcn_type == 'classmethod':
                        setattr(new_class.__class__, attr[0], attr[1])
                    else:  # standard instance function
                        # we have to use function.im_func to avoid explicit 'self' enforcement
                        setattr(new_class, attr[0], attr[1].im_func)
                except KeyError:  # some things like __repr__, etc..
                    pass

            # attach the new klass to this class
            setattr(cls, new_class.__name__, new_class)

            # add the proxy method to the graph and update this klass as the proxy to the proxy.
            cls._GRAPH.add_proxy(cls.__name__.lower(), new_class)
            cls._PROXY = getattr(cls._GRAPH, cls.__name__.lower())
            # next add back in the callable(s) to this proxy
            bulbs_proxy_model_fcns = inspect.getmembers(cls._PROXY,
                                                        lambda b: inspect.isroutine(b) or inspect.isdatadescriptor(b))
            bulbs_proxy_model_fcns = [a for a in bulbs_proxy_model_fcns if not(a[0] in blacklist)]
            for fcn in bulbs_proxy_model_fcns:
                setattr(cls, fcn[0], fcn[1])
            cls._WRAPPED_KLASS = new_class

            ## Add groovy script automatic inclusion, loading, and method setting
            #process:
            #   load groovy scripts into the _GRAPH instance
            #   make all classmethod, since arguments are unknown and not always related to the instance.
            if cls._SCRIPTS and isinstance(cls._SCRIPTS, (list, tuple)):
                #try:
                # first get the path for the class
                filepath = ospath.dirname(ospath.abspath(inspect.getfile(cls)))
                filepath = ospath.join(filepath, 'groovy')
                for gsn in cls._SCRIPTS:
                    # our result path per that groovy script associated to that model
                    if not gsn.endswith('.groovy'):
                        groovyScriptFile = ospath.join(filepath, gsn + '.groovy')
                    else:
                        groovyScriptFile = ospath.join(filepath, gsn)
                    print groovyScriptFile
                    # add the script to the graph
                    cls._GRAPH.scripts.update(groovyScriptFile)
                    # now lets add the classmethods to the wrapper model as classmethods
                    with app.open_resource(groovyScriptFile, 'r') as f:
                        # first we have to find the functions, these should start with regex '^def', sub functions
                        # or space padded functions will be ignored
                        prevLine = ''
                        for line in f.readlines():
                            # also ignore manual 'no-include' commented functions
                            if line.startswith('def') and not 'no-include' in prevLine:
                                func_name = line.lstrip('def ').split('(')[0]

                                # lets define the new function
                                if 'is-raw' in prevLine:  # Returns raw results
                                    def new_func(kls, **kwargs):
                                        fcn_name = copy(func_name)
                                        name_spc = copy(gsn)
                                        script = kls._GRAPH.scripts.get(fcn_name, name_spc)
                                        params = dict([('element_type', kls.element_type), ] + kwargs.items())
                                        return kls._GRAPH.gremlin.execute(script, params)
                                elif 'is-single-raw' in prevLine:
                                    def new_func(kls, **kwargs):
                                        fcn_name = copy(func_name)
                                        name_spc = copy(gsn)
                                        script = kls._GRAPH.scripts.get(fcn_name, name_spc)
                                        params = dict([('element_type', kls.element_type), ] + kwargs.items())
                                        return kls._GRAPH.gremlin.command(script, params)
                                else:  # assume it is of type Vertex, Edge, Node or Relationship
                                    def new_func(kls, **kwargs):
                                        fcn_name = copy(func_name)
                                        name_spc = copy(gsn)
                                        script = kls._GRAPH.scripts.get(fcn_name, name_spc)
                                        params = dict([('element_type', kls.element_type), ] + kwargs.items())
                                        return kls._GRAPH.gremlin.query(script, params)
                                # set the docstring so we know this is a dynamically loaded groovy method
                                new_func.__doc__ = 'Groovy Script: %s.%s' % (cls.__name__, func_name)
                                setattr(cls, func_name, classmethod(new_func))
                            prevLine = line

    @classmethod
    def all(cls, *args, **kwargs):
        """ Easy access to all nodes or relationships defined by a given model

        An easy way to utilize MyModel.all
        """
        return cls._PROXY.get_all(*args, **kwargs)

    @classmethod
    def get(cls, eid):
        """ Get an Vertex/Edge based on the EID

        Shortcut for MyModel._PROXY.get
        """
        return cls._PROXY.get(eid)

    @classmethod
    def lookup(cls, raw_query=False, **kwargs):
        """ Gets Vertex/Edge(s) based on kwargs only

        Shortcut for MyModel.PROXY.index.lookup
        """
        obj = cls._PROXY.index.lookup(**kwargs)
        logger.debug("Got data from lookup: %s" % obj)
        if not obj and raw_query:
            raise cls.DoesNotExist('Object does not exist: %s' % (repr(kwargs)))
        return obj

    @classmethod
    def lookup_single(cls, raw_query=False, **kwargs):
        query = cls.lookup(raw_query=raw_query, **kwargs)
        if isinstance(query, GeneratorType):
            return query.next()
        return query

    class DoesNotExist(Exception):
        pass


class Node(BulbsWrapper):

    _NODE_KLASS = BulbsNode


class Relationship(BulbsWrapper):

    _NODE_KLASS = BulbsRelationship

    @classmethod
    def all(cls, reference_vertex, edge_dir='out', *args, **kwargs):
        """ Easy access to all nodes or relationships defined by a given model

        An easy way to utilize MyModel.all

        This is a bugfix to current bulb flow code. This normally doesn't return properly

        @param reference_vertex: a reference vertex from the outE relationship
            @type reference_vertex: Node
        @param edge_dir: Edge direction. Possible values are `out`, `in` or `both`. Default assumes we are referencing a
                         node to get edges going out of the reference vertex
            @type edge_dir: str
        @return GeneratorType
        """
        proxy_config = cls._PROXY.client.config
        label = cls._PROXY.element_class.get_label(proxy_config)
        if edge_dir.lower() in 'out':
            script = "g.v(id).outE(label)"
        elif edge_dir.lower() == 'in':
            script = "g.v(id).inE(label)"
        else:
            script = "g.v(id).bothE(label)"

        return cls._GRAPH.gremlin.query(script, {'id': reference_vertex.eid, 'label': label})


def configure_models(app, module):

    def predicate(klass, mod=module):
        """Predicate to make sure imported classes are only from the module in question and are a subclass of our own
        Node and Relationship types
        """
        try:
            return inspect.isclass(klass) and \
                klass.__module__ == mod.__name__ and \
                (issubclass(klass, Node) or issubclass(klass, Relationship))
        except:
            return False

    klasses = inspect.getmembers(module, predicate)
    models = {}
    print "Setting up classes: [",
    for klass_name, kls in klasses:
        logger.debug("Setting up %s.%s" % (module.__name__, kls.__name__))
        print "%s.%s," % (module.__name__, kls.__name__),
        kls._setup_klass_(app)
        models[kls.__name__] = kls
    print "]"
    return models


def configure_module_groovy_scripts(app, module, scripts):
    try:
        # first get the path for the class
        filepath = ospath.dirname(ospath.abspath(inspect.getfile(module)))
        for gsn in scripts:
            # our result path per that groovy script associated to that model
            if not gsn.startswith('groovy'):
                groovyScriptFile = ospath.join(ospath.join(filepath, 'groovy'), gsn)
            else:
                groovyScriptFile = ospath.join(filepath, gsn)
            # add the script to the graph
            app.config['DATABASE'].scripts.update(groovyScriptFile)
    except Exception as e:
        logger.warning("Error loading groovy script from module %s: %s" % (module, e))
