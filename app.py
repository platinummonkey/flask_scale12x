from flask import abort
from flask.ext.environments import Environments
from tools.sessions import CachedFlask, setup_sessioned_app
from tools.login_manager import TokenSessionLoginManager, setup_login_manager

import logging

logger = logging.getLogger(__name__)

has_loaded = False
if not has_loaded:
    root_module = __name__.split('.')[0]

    # Setup App
    app = CachedFlask(root_module)
    env = Environments(app, default_env='DEVELOPMENT')
    env.from_object('config')

    print "Running in environment: %s" % env.env

    session_key = app.config.get('SESSION_SECRET_KEY', '')
    if not env.env.lower().startswith('development'):
        # Setup Sessions and Caching
        session_cache_config = app.config.get('SESSION_CACHE_CONFIG', None)
        app_cache_config = app.config.get('APP_CACHE_CONFIG', None)

        setup_sessioned_app(app=app,
                            session_key=session_key,
                            session_cache_config=session_cache_config,
                            app_cache_config=app_cache_config)

        session_cache = app.config.get('_session_cache')
        cache = app.config.get('_app_cache')
    else:
        setup_sessioned_app(app=app, session_key=session_key, debug=True)

        ### Import urls from list of <config>.INSTALLED_APPS

        # login manager
        login_manager = TokenSessionLoginManager()
        login_manager.init_app(app)
        login_manager = setup_login_manager(login_manager)
    
    # Add custom Error Handlers
    @app.errorhandler(404)
    def not_found(error):
        logger.info(error)
        abort(404)

    @app.errorhandler(403)
    def unauthorized(error):
        logger.info(error)
        abort(403)

    @app.errorhandler(500)
    def server_error(error):
        logger.error(error)
        abort(500)

    has_loaded = True


__all__ = ['app', 'root_module', 'login_manager']
