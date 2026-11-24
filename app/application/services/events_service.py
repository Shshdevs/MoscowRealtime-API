from datetime import datetime, timedelta, timezone

from geopy.distance import geodesic

from app.domain.models.event import Event
from app.infrastructure.events.events_data_source import EventsDataSource


class EventsService:
    _CITY = "Москва"
    _PAGE_SIZE = 100
    _NEARBY_SCAN_LIMIT = 500

    def __init__(self, data_source: EventsDataSource):
        self.data_source = data_source

    def get_events(self, limit: int, skip: int) -> tuple[int, list[Event]]:
        now = datetime.now(timezone.utc)
        starts_at_min, starts_at_max = self._window(now, days=30)
        return self.data_source.fetch_events_page(
            city=self._CITY,
            starts_at_min=starts_at_min,
            starts_at_max=starts_at_max,
            limit=limit,
            skip=skip,
        )

    def get_nearby_events(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int,
    ) -> list[Event]:
        now = datetime.now(timezone.utc)
        starts_at_min, starts_at_max = self._window(now, days=7)
        pages_to_scan = self._NEARBY_SCAN_LIMIT // self._PAGE_SIZE
        total = 0
        events: list[Event] = []

        for page in range(pages_to_scan):
            page_total, page_events = self.data_source.fetch_events_page(
                city=self._CITY,
                starts_at_min=starts_at_min,
                starts_at_max=starts_at_max,
                limit=self._PAGE_SIZE,
                skip=page * self._PAGE_SIZE,
            )
            total = page_total
            events.extend(page_events)
            if len(events) >= total or len(page_events) < self._PAGE_SIZE:
                break

        origin = (latitude, longitude)
        matches = []
        for event in events:
            if not self._is_upcoming(event, now) or event.venue is None:
                continue
            if event.venue.latitude is None or event.venue.longitude is None:
                continue
            distance = geodesic(
                origin,
                (event.venue.latitude, event.venue.longitude),
            ).meters
            if distance <= radius_meters:
                matches.append(event)
        return matches

    def get_event(self, event_id: int) -> Event:
        return self.data_source.fetch_event(event_id)

    @staticmethod
    def _window(now: datetime, days: int) -> tuple[str, str]:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=days)
        return start.isoformat(), end.isoformat()

    @staticmethod
    def _is_upcoming(event: Event, now: datetime) -> bool:
        if not event.dates:
            return True
        return event.dates[0].start >= int(now.timestamp() * 1000)
