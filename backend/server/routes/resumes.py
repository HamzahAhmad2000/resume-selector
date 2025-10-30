from flask import Blueprint, jsonify, request

from ..services.resume_service import ingest_resume

resumes_bp = Blueprint('resumes', __name__)


@resumes_bp.route('/resumes', methods=['POST'])
def upload_resume_endpoint():
    storage = request.files.get('file')
    if storage is None:
        return jsonify({'error': 'file is required'}), 400
    try:
        result = ingest_resume(storage)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    return jsonify(result), 200
