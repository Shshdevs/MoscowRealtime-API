import logging

from flask import Blueprint, current_app, jsonify, request


logger = logging.getLogger(__name__)

analysis_bp = Blueprint("analysis", __name__)

@analysis_bp.route("/analyze", methods=["POST"])
def analyze_image():
    try:
        service = current_app.container["image_analysis_service"]
        detector = current_app.container["detector"]

        if not detector.is_loaded():
            return jsonify({
                "success": False,
                "error": "YOLO модель не загружена",
            }), 503

        user_id = request.args.get("userId") or request.form.get("userId")
        img_path = request.args.get("imgPath") or request.form.get("imgPath")

        if not img_path:
            return jsonify({
                "success": False,
                "error": "Missing imgPath",
            }), 400

        result = service.analyze(
            img_path=img_path,
            user_id=user_id,
        )

        if result.get("success") is False:
            status_code = result.pop("status_code", 400)
            return jsonify(result), status_code

        result.pop("labels", None)
        return jsonify(result), 200

    except ValueError as exc:
        logger.warning("Bad analyze request: %s", exc)
        return jsonify({
            "success": False,
            "error": str(exc),
        }), 400

    except RuntimeError as exc:
        logger.error("Service unavailable: %s", exc)
        return jsonify({
            "success": False,
            "error": str(exc),
        }), 503

    except Exception as exc:
        logger.exception("Analyze request failed: %s", exc)
        return jsonify({
            "success": False,
            "error": "Internal server error",
        }), 500
