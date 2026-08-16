from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .api import api_bp
from .extensions import db, migrate


def _register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return jsonify(error=error.description), error.code

    # In tests, let unexpected exceptions propagate so failures surface with a
    # traceback instead of a swallowed 500.
    if not app.config.get('TESTING'):
        @app.errorhandler(Exception)
        def handle_unexpected(error):
            app.logger.exception('Unhandled exception')
            return jsonify(error='Internal server error'), 500


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    CORS(app, resources={"/*": {"origins": config.ALLOWED_ORIGIN}})
    db.init_app(app)
    migrate.init_app(app, db)
    _register_error_handlers(app)
    app.register_blueprint(api_bp)
    return app
