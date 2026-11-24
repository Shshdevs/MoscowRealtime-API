import logging
from typing import cast

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import JSONResponse

from app.container import ApplicationContainer

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze")
def analyze_image(
    request: Request,
    user_id_query: str | None = Query(default=None, alias="userId"),
    img_path_query: str | None = Query(default=None, alias="imgPath"),
    user_id_form: str | None = Form(default=None, alias="userId"),
    img_path_form: str | None = Form(default=None, alias="imgPath"),
):
    try:
        container = cast(ApplicationContainer, request.app.state.container)
        service = container["image_analysis_service"]
        detector = container["detector"]
        if not detector.is_loaded():
            return JSONResponse(
                {"success": False, "error": "YOLO модель не загружена"}, status_code=503
            )
        user_id = user_id_query or user_id_form
        img_path = img_path_query or img_path_form
        if not img_path:
            return JSONResponse(
                {"success": False, "error": "Missing imgPath"}, status_code=400
            )
        result = service.analyze(img_path=img_path, user_id=user_id)
        if result.get("success") is False:
            status_code = result.pop("status_code", 400)
            return JSONResponse(result, status_code=status_code)
        return result
    except ValueError as exc:
        logger.warning("Bad analyze request: %s", exc)
        return JSONResponse({"success": False, "error": str(exc)}, status_code=400)
    except RuntimeError as exc:
        logger.error("Service unavailable: %s", exc)
        return JSONResponse({"success": False, "error": str(exc)}, status_code=503)
