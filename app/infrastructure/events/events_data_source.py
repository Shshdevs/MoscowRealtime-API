import logging
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from threading import Lock, RLock
from typing import Any

import httpx
from cachetools import TTLCache

from app.domain.models.event import Event, EventDate, EventVenue

logger = logging.getLogger(__name__)


class EventsSourceError(RuntimeError):
    pass


class EventsSourceUnavailable(EventsSourceError):
    pass


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text:
            self.parts.append(text)


class EventsDataSource:
    _BASE_URL = "https://api.timepad.ru/v1/"
    _FIELDS = "location,registration_data,description_short,description_html,poster_image,age_limit"

    def __init__(self, api_token: str | None):
        self._api_token = api_token.strip() if api_token else ""
        self._client = httpx.Client(
            base_url=self._BASE_URL,
            headers={
                "Accept": "application/json",
                **({"Authorization": f"Bearer {self._api_token}"} if self._api_token else {}),
            },
            timeout=httpx.Timeout(12.0),
            follow_redirects=False,
        )
        self._cache: TTLCache[tuple[Any, ...], Any] = TTLCache[tuple[Any, ...], Any](maxsize=256, ttl=300)
        self._cache_lock = RLock()
        self._request_lock = Lock()
        self._last_request_at = 0.0

    def close(self) -> None:
        self._client.close()

    def fetch_events_page(
        self,
        city: str,
        starts_at_min: str,
        starts_at_max: str,
        limit: int,
        skip: int,
    ) -> tuple[int, list[Event]]:
        safe_limit = min(max(limit, 1), 100)
        safe_skip = max(skip, 0)
        cache_key = ("page", city, starts_at_min, starts_at_max, safe_limit, safe_skip)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        payload = self._request_json(
            "events.json",
            {
                "limit": safe_limit,
                "skip": safe_skip,
                "cities": city,
                "sort": "+starts_at",
                "fields": self._FIELDS,
                "starts_at_min": starts_at_min,
                "starts_at_max": starts_at_max,
            },
        )
        values = payload.get("values")
        if not isinstance(values, list):
            raise EventsSourceError("Events source returned an invalid response")
        try:
            total = int(payload.get("total", 0))
        except (TypeError, ValueError):
            total = 0
        result = (total, [self._map_event(item) for item in values if isinstance(item, dict)])
        self._set_cached(cache_key, result)
        return result

    def fetch_event(self, event_id: int) -> Event:
        cache_key = ("event", event_id)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        payload = self._request_json(
            f"events/{event_id}",
            {"fields": self._FIELDS},
        )
        if not isinstance(payload, dict) or "id" not in payload:
            raise EventsSourceError("Events source returned an invalid event")
        event = self._map_event(payload)
        self._set_cached(cache_key, event)
        return event

    def _request_json(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        if not self._api_token:
            raise EventsSourceUnavailable("Events source is not configured")

        with self._request_lock:
            wait_seconds = 1.0 - (time.monotonic() - self._last_request_at)
            if wait_seconds > 0:
                time.sleep(wait_seconds)
            try:
                response = self._client.get(path, params=params)
                self._last_request_at = time.monotonic()
                response.raise_for_status()
                payload = response.json()
            except httpx.HTTPStatusError as exc:
                logger.warning("Events source returned HTTP %s", exc.response.status_code)
                raise EventsSourceError("Events source request failed") from None
            except (httpx.HTTPError, ValueError):
                logger.warning("Events source request failed")
                raise EventsSourceError("Events source request failed") from None

        if not isinstance(payload, dict):
            raise EventsSourceError("Events source returned an invalid response")
        return payload

    def _get_cached(self, key: tuple[Any, ...]) -> Any | None:
        with self._cache_lock:
            try:
                return self._cache[key]
            except KeyError:
                return None

    def _set_cached(self, key: tuple[Any, ...], value: Any) -> None:
        with self._cache_lock:
            self._cache[key] = value

    @classmethod
    def _map_event(cls, item: dict[str, Any]) -> Event:
        start = cls._timestamp(item.get("starts_at"))
        end = cls._timestamp(item.get("ends_at"))
        dates = (EventDate(start, end or start),) if start is not None else ()
        location = item.get("location") if isinstance(item.get("location"), dict) else {}
        coordinates = location.get("coordinates")
        latitude = cls._as_float(coordinates[0]) if isinstance(coordinates, list) and len(coordinates) > 1 else None
        longitude = cls._as_float(coordinates[1]) if isinstance(coordinates, list) and len(coordinates) > 1 else None
        venue = None
        if location.get("city") or location.get("address") or latitude is not None or longitude is not None:
            venue = EventVenue(
                city=location.get("city"),
                address=location.get("address"),
                latitude=latitude,
                longitude=longitude,
            )

        registration = item.get("registration_data")
        registration = registration if isinstance(registration, dict) else {}
        price_min = cls._as_float(registration.get("price_min"))
        price_max = cls._as_float(registration.get("price_max"))
        poster = item.get("poster_image")
        poster = poster if isinstance(poster, dict) else {}
        categories = item.get("categories")
        categories = categories if isinstance(categories, list) else []
        description_html = item.get("description_html") or ""
        description = item.get("description_short") or cls._plain_text(description_html)

        return Event(
            id=int(item["id"]),
            title=str(item.get("name") or ""),
            description=str(description),
            body_text=cls._plain_text(description_html),
            dates=dates,
            categories=tuple(
                str(category["name"])
                for category in categories
                if isinstance(category, dict) and category.get("name")
            ),
            age_restriction=item.get("age_limit"),
            price_min=price_min,
            price_max=price_max,
            is_free=price_min == 0 or (price_min is None and price_max == 0),
            image_url=poster.get("default_url") or poster.get("uploadcare_url"),
            site_url=str(item.get("url") or ""),
            venue=venue,
        )

    @staticmethod
    def _timestamp(value: Any) -> int | None:
        if not value:
            return None
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return int(parsed.timestamp() * 1000)

    @staticmethod
    def _as_float(value: Any) -> float | None:
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _plain_text(value: str) -> str:
        parser = _TextExtractor()
        parser.feed(value)
        return " ".join(parser.parts)
