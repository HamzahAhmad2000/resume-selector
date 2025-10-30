from flask import Blueprint, send_from_directory

from ..config import UPLOAD_DIR

uploads_bp = Blueprint('uploads', __name__)


@uploads_bp.route('/uploads/<path:filename>', methods=['GET'])
def serve_upload(filename: str):
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=False)
