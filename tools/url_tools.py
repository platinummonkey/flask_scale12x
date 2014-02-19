from werkzeug.utils import import_string, cached_property
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
import logging

logger = logging.getLogger(__name__)


def module_name(name):
    return name.split('.')[0]


## Lazy Loaded cached view
class CachedView(object):

    def __init__(self, import_name):
        self.__module__, self.__name__ = import_name.rsplit('.', 1)
        self.__module__ = self.__module__.lstrip('.')
        self.import_name = import_name.lstrip('.')
        if hasattr(self.view, 'methods'):
            self.methods = self.view.methods
        if hasattr(self.view, 'view_class'):
            self.view_class = self.view.view_class

    @cached_property
    def view(self):
        logger.debug("Importing and caching view: %s" % self.import_name)
        return import_string(self.import_name)

    def __call__(self, *args, **kwargs):
        return self.view(*args, **kwargs)


def url(blueprint, url_rule, view_func, **options):
    """ Wrap the view function in a LazyView so it's only loaded on demand

    Example url rule:
        # ( <str: route>, <str: view>, <dict: options>)
        ('/', 'views.hello', {'some_option': 'some_value'}),

    @param blueprint: Blueprint reference
        @type blueprint: flask.Blueprint
    @param url_rule
    """
    view = CachedView(view_func)
    endpoint = options.pop("endpoint", view.__name__)
    blueprint.add_url_rule(url_rule, endpoint, view, **options)


def url_configure(blueprint, prefix, *urls):
    """ Django-like url pattern specification for Flask

    Example urls.py:
        # Setup Blueprint
        urls = Blueprint('accounts_url', module_name(__name__))

        # define URLS here
        url_configure(urls, '',
            # ( <str: route>, <str: view>, <dict: options>)
            ('/', 'views.hello', {'some_option': 'some_value'}),
        )

    @param blueprint: Blueprint reference
        @type blueprint: flask.Blueprint
    @param prefix:  URL prefix to append to all subsequent url rules
        @type prefix: str
    @param urls: List of tuples that contain the url rules. See example above
        @type urls: tuple(str, str, dict)
    @returns: None
    """

    assert isinstance(prefix, (str, unicode, basestring)), "Prefix must be a string"
    prefix = prefix.rstrip().rstrip('.') + '.'
    for url_spec in urls:
        assert isinstance(url_spec, (tuple, list)) and len(url_spec) >= 2, "URL Rules must be a tuple"
        rule = url_spec[0]
        view_func = prefix + url_spec[1]
        if len(url_spec) > 2:
            options = url_spec[2]
            assert isinstance(options, dict), "Options must be a dict"
        else:
            options = {}
        url(blueprint, rule, view_func, **options)

