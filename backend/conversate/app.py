from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .api import api_blueprints
from .extensions import db, limiter, migrate


def _register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return jsonify(error=error.description), error.code

    # In tests, let unexpected errors raise, so they show a traceback.
    if not app.config.get('TESTING'):

        @app.errorhandler(Exception)
        def handle_unexpected(error):
            app.logger.exception('Unhandled exception')
            return jsonify(error='Internal server error'), 500


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    CORS(app, resources={'/*': {'origins': config.ALLOWED_ORIGIN}})
    db.init_app(app)
    migrate.init_app(app, db)
    # Off under TESTING; the rate-limit test turns it back on.
    app.config.setdefault('RATELIMIT_ENABLED', not app.config.get('TESTING', False))
    limiter.init_app(app)
    _register_error_handlers(app)
    for blueprint in api_blueprints:
        app.register_blueprint(blueprint)
    return app
