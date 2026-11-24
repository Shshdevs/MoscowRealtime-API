from typing import cast

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from app.container import ApplicationContainer
from app.api.schemas.responses import ClosestLocationResponse

router = APIRouter()


@router.get("/closest")
def get_closest_to_user(
    request: Request,
    lat: float | None = Query(default=None),
    lon: float | None = Query(default=None),
):
    if lat is None or lon is None:
        return JSONResponse(
            {"success": False, "error": "Missing coordinates"}, status_code=400
        )

    container = cast(ApplicationContainer, request.app.state.container)
    service = container["location_service"]
    result = service.get_closest(lat=lat, lon=lon)
    if "error" in result:
        return JSONResponse(
            {"success": False, "error": result["error"]}, status_code=404
        )
    return ClosestLocationResponse(
        closest_location=result["closest_loc"],
        distance=result["distance"],
    ).model_dump()
