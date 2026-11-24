from typing import cast

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from app.api.schemas.responses import (
    EventDateResponse,
    EventDetailResponse,
    EventResponse,
    EventsResponse,
    EventVenueResponse,
)
from app.application.services.events_service import EventsService
from app.container import ApplicationContainer
from app.infrastructure.events.events_data_source import (
    EventsSourceError,
    EventsSourceUnavailable,
)

router = APIRouter()


@router.get("/events")
def get_events(
    request: Request,
    limit: int = Query(default=100, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
):
    service = _service(request)
    try:
        total, events = service.get_events(limit=limit, skip=skip)
    except EventsSourceUnavailable:
        return _source_error("Event source is not configured", 503)
    except EventsSourceError:
        return _source_error("Event source is temporarily unavailable", 502)
    return EventsResponse(total=total, events=[_event_response(event) for event in events]).model_dump()


@router.get("/events/nearby")
def get_nearby_events(
    request: Request,
    lat: float = Query(ge=-90, le=90),
    lon: float = Query(ge=-180, le=180),
    radius: int = Query(default=1000, ge=1, le=50000),
):
    service = _service(request)
    try:
        events = service.get_nearby_events(
            latitude=lat,
            longitude=lon,
            radius_meters=radius,
        )
    except EventsSourceUnavailable:
        return _source_error("Event source is not configured", 503)
    except EventsSourceError:
        return _source_error("Event source is temporarily unavailable", 502)
    return EventsResponse(total=len(events), events=[_event_response(event) for event in events]).model_dump()


@router.get("/events/{event_id}")
def get_event(request: Request, event_id: int):
    service = _service(request)
    try:
        event = service.get_event(event_id)
    except EventsSourceUnavailable:
        return _source_error("Event source is not configured", 503)
    except EventsSourceError:
        return _source_error("Event source is temporarily unavailable", 502)
    return EventDetailResponse(event=_event_response(event)).model_dump()


def _service(request: Request) -> EventsService:
    container = cast(ApplicationContainer, request.app.state.container)
    return container["events_service"]


def _source_error(message: str, status_code: int) -> JSONResponse:
    return JSONResponse({"success": False, "error": message}, status_code=status_code)


def _event_response(event) -> EventResponse:
    venue = None
    if event.venue is not None:
        venue = EventVenueResponse(
            city=event.venue.city,
            address=event.venue.address,
            latitude=event.venue.latitude,
            longitude=event.venue.longitude,
        )
    return EventResponse(
        id=event.id,
        title=event.title,
        description=event.description,
        body_text=event.body_text,
        dates=[EventDateResponse(start=date.start, end=date.end) for date in event.dates],
        categories=list(event.categories),
        age_restriction=event.age_restriction,
        price_min=event.price_min,
        price_max=event.price_max,
        is_free=event.is_free,
        image_url=event.image_url,
        site_url=event.site_url,
        venue=venue,
    )
