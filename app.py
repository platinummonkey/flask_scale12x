from flask import Flask, abort

import logging

logger = logging.getLogger(__name__)

has_loaded = False
if not has_loaded:
    root_module = __name__.split('.')[0]

    # Setup App
    app = Flask(root_module)
    
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


__all__ = ['app', 'root_module']
