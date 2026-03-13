from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from container import build_container
from presentation.api.routes.analysis import analysis_bp
from presentation.api.routes.health import health_bp
from presentation.api.routes.location import location_bp
from presentation.api.middleware import register_middlewares
from config import Config


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_port=1,
    )

    app.config["MAX_CONTENT_LENGTH"] = Config.MAX_CONTENT_LENGTH

    app.container = build_container()

    CORS(
        app,
        resources={
            r"/*": {
                "origins": ["*"],
                "methods": ["GET", "POST"],
                "allow_headers": ["Content-Type", "Authorization"],
            }
        },
    )

    register_middlewares(app)

    app.register_blueprint(health_bp)
    app.register_blueprint(location_bp)
    app.register_blueprint(analysis_bp)

    register_error_handlers(app)

    return app


def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": "Bad request"}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": "Endpoint not found"}), 404

    @app.errorhandler(413)
    def too_large(error):
        return jsonify({"success": False, "error": "File too large"}), 413

    @app.errorhandler(429)
    def too_many_requests(error):
        return jsonify({"success": False, "error": "Too many requests"}), 429

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"success": False, "error": "Internal server error"}), 500
