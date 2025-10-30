from flask import Blueprint, jsonify, request

from ..services.feedback_service import apply_feedback
from .schemas import FeedbackPayload

feedback_bp = Blueprint('feedback', __name__)


@feedback_bp.route('/feedback', methods=['POST'])
def feedback_endpoint():
    data = request.get_json(silent=True) or {}
    payload = FeedbackPayload(**data)
    try:
        result = apply_feedback(payload.job_id, payload.shown_candidate_ids, payload.chosen_candidate_id)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    return jsonify(result), 200
