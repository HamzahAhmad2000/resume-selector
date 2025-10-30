from flask import Flask, jsonify
from flask_cors import CORS
from pydantic import ValidationError

from .config import ALLOWED_ORIGINS
from .database import init_db
from .routes.feedback import feedback_bp
from .routes.health import health_bp
from .routes.jobs import jobs_bp
from .routes.models import models_bp
from .routes.rankings import rankings_bp
from .routes.resumes import resumes_bp
from .routes.uploads import uploads_bp


def create_app() -> Flask:
    init_db()
    app = Flask(__name__)
    CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=False)

    app.register_blueprint(health_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(resumes_bp)
    app.register_blueprint(rankings_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(models_bp)
    app.register_blueprint(uploads_bp)

    @app.errorhandler(ValidationError)
    def handle_validation_error(err: ValidationError):  # pragma: no cover - simple glue
        return jsonify({'error': err.errors()}), 400

    @app.errorhandler(ValueError)
    def handle_value_error(err: ValueError):  # pragma: no cover - simple glue
        return jsonify({'error': str(err)}), 400

    return app
