from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from ..services.job_service import create_job
from .schemas import JobPayload

jobs_bp = Blueprint('jobs', __name__)


@jobs_bp.route('/jobs', methods=['POST'])
def create_job_endpoint():
    data = request.get_json(silent=True) or {}
    payload = JobPayload(**data)
    job_id = create_job(payload.title, payload.description)
    return jsonify({'job_id': job_id}), 200
