from werkzeug.utils import import_string, ImportStringError
import logging
from app import app

logger = logging.getLogger(__name__)


def installed_apps_loader(flask_app, installed_apps):
    """ INSTALLED_APPS loader utility.

    This enables us to use Django-style url loading via the config options

    Ex: INSTALLED_APPS = (
        '',                  # will load the <app_root>.urls,  this will not prefix the urls.
        ('auth', '/auth'),   # will load the `auth.urls` module into it's urls and prefix all the urls with '/auth'
    )

    where tuple form is defined as: (<str:app_name>, <str:url_prefix>)
    """
    #setattr(app_globals, '_APP_MODELS', {})
    app.config['__APP_MODELS'] = {}
    #app_models = getattr(app_globals, '_APP_MODELS', {})
    assert isinstance(installed_apps, (tuple, list)), "INSTALLED_APPS must be a tuple"
    for new_app_spec in installed_apps:
        # If we hae a list, it is expected to be in (<app_name>, <url_prefix>) form.
        if isinstance(new_app_spec, (tuple, list)):
            assert len(new_app_spec) == 2, "app spec must be a tuple of length 2"
            new_app = new_app_spec[0]
            url_prefix = new_app_spec[1]
        else:  # we only have an `app_name` so use this with no `url_prefix`
            new_app = new_app_spec
            assert isinstance(new_app, (str, unicode)), "app must be a string"
            url_prefix = ''
        #print "started with app name: '%s' and url_prefix: '%s'" % (new_app, url_prefix)
        url_module = new_app
        while not url_module.endswith(".urls.urls"):
            url_module += '.urls'

        # fix relative import as well
        url_module = url_module.lstrip('.')

        ## Setup URLS
        # don't assume we have a urls.py, it may just be a collection of models
        try:
            urls = import_string(url_module)
            flask_app.register_blueprint(urls, url_prefix=url_prefix)
        except (ImportError, ImportStringError):
            logger.info("No urls.py found for app %s, abandoning import" % new_app)


__all__ = ['installed_apps_loader']
