from flask import Blueprint, jsonify

from ..services.model_state_service import fetch_model_state

models_bp = Blueprint('models', __name__)


@models_bp.route('/models', methods=['GET'])
def get_model_state():
    return jsonify(fetch_model_state()), 200
