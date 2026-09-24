from flask import Blueprint, jsonify

from .accounts import accounts_bp
from .quiz import quiz_bp
from .speech import speech_bp

health_bp = Blueprint('health_bp', __name__)


@health_bp.route('/health')
def health():
    return jsonify(status='ok'), 200


api_blueprints = (health_bp, accounts_bp, quiz_bp, speech_bp)
