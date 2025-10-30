from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check() -> tuple:
    return jsonify({'ok': True}), 200
