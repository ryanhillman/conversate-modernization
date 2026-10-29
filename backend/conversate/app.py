from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .api import api_blueprints
from .extensions import db, limiter, migrate


def _register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        # The error's own response keeps its headers, such as Allow on a 405.
        response = error.get_response()
        response.data = app.json.dumps({'error': error.description})
        response.content_type = 'application/json'
        return response

    # In tests, let unexpected errors raise, so they show a traceback.
    if not app.config.get('TESTING'):

        @app.errorhandler(Exception)
        def handle_unexpected(error):
            app.logger.exception('Unhandled exception')
            return jsonify(error='Internal server error'), 500


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    CORS(app, origins=config.ALLOWED_ORIGIN)
    db.init_app(app)
    migrate.init_app(app, db)
    # Counts live in this process, which is correct only while the backend runs
    # as one process (see the Dockerfile).
    app.config.setdefault('RATELIMIT_STORAGE_URI', 'memory://')
    limiter.init_app(app)
    _register_error_handlers(app)
    for blueprint in api_blueprints:
        app.register_blueprint(blueprint)
    return app
