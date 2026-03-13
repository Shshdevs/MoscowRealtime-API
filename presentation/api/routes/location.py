from flask import Blueprint, current_app, jsonify, request

location_bp = Blueprint("location", __name__)


@location_bp.route("/closest", methods=["GET"])
def get_closest_to_user():
    try:
        lat = request.args.get("lat", type=float)
        lon = request.args.get("lon", type=float)

        if lat is None or lon is None:
            return jsonify({
                "success": False,
                "error": "Missing coordinates"
            }), 400

        service = current_app.container["location_service"]
        result = service.get_closest(lat=lat, lon=lon)

        if "error" in result:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 404

        return jsonify({
            "success": True,
            "closest_location": result["closest_loc"],
            "distance": result["distance"]
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500
