from werkzeug.utils import import_string, ImportStringError
from bulbs_wrapper import configure_models, configure_module_groovy_scripts
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
        models_module = new_app + '.models'

        # fix relative import as well
        url_module = url_module.lstrip('.')
        models_module = models_module.lstrip('.')
        module_groovy_scripts = (new_app + '.GROOVY_SCRIPTS').lstrip('.')
        

        ## Setup URLS
        # don't assume we have a urls.py, it may just be a collection of models
        try:
            urls = import_string(url_module)
            flask_app.register_blueprint(urls, url_prefix=url_prefix)
        except (ImportError, ImportStringError):
            logger.info("No urls.py found for app %s, abandoning import" % new_app)

        ## install groovy scripts for the app
        try:
            groovy_scripts = import_string(module_groovy_scripts)
            assert isinstance(groovy_scripts, (tuple, list)), "GROOVY_SCRIPTS for %s must be a tuple!" % new_app
            configure_module_groovy_scripts(app, new_app, groovy_scripts)
        except (ImportError, ImportStringError):
            logger.info("No GROOVY_SCRIPTS found for app %s" % new_app)

        ## setup OGM classes for our graph context
        # don't assume we have a models.py, it may just be a collection of views
        try:
            logger.debug("trying to import models module: %s" % models_module)
            print "trying to import models module: %s => " % models_module,
            module = import_string(models_module)
            #print "loaded models.py, trying to load models",
            loaded_models = configure_models(app, module)
            #print "loaded models: %s" % (loaded_models),
            #app_models['__APP_MODELS'][new_app] = loaded_models
            app.config['__APP_MODELS'][new_app] = loaded_models
            print "successfully imported models"
        except (ImportError, ImportStringError, TypeError):
            logger.info("No models.py found for app %s, abandoning import" % new_app)
            print "No models.py found for app %s, abandoning import" % new_app

__all__ = ['installed_apps_loader']
