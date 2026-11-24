from dataclasses import dataclass


@dataclass(frozen=True)
class EventDate:
    start: int
    end: int


@dataclass(frozen=True)
class EventVenue:
    city: str | None
    address: str | None
    latitude: float | None
    longitude: float | None


@dataclass(frozen=True)
class Event:
    id: int
    title: str
    description: str
    body_text: str
    dates: tuple[EventDate, ...]
    categories: tuple[str, ...]
    age_restriction: str | None
    price_min: float | None
    price_max: float | None
    is_free: bool
    image_url: str | None
    site_url: str
    venue: EventVenue | None
