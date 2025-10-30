from flask import Blueprint, jsonify, request

from ..services.ranking_service import fetch_rankings

rankings_bp = Blueprint('rankings', __name__)


@rankings_bp.route('/rankings', methods=['GET'])
def rankings_endpoint():
    job_id_raw = request.args.get('job_id')
    if job_id_raw is None:
        return jsonify({'error': 'job_id is required'}), 400
    try:
        job_id = int(job_id_raw)
    except ValueError:
        return jsonify({'error': 'job_id must be an integer'}), 400
    try:
        k = int(request.args.get('k', 5))
    except ValueError:
        return jsonify({'error': 'k must be an integer'}), 400
    try:
        epsilon = float(request.args.get('epsilon', 0.1))
    except ValueError:
        return jsonify({'error': 'epsilon must be numeric'}), 400

    data = fetch_rankings(job_id, k, epsilon)
    return jsonify({'job_id': job_id, **data}), 200
