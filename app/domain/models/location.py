from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    id: str
    name: str
    latitude: float
    longitude: float


@dataclass(frozen=True)
class NearestLocation:
    location: dict
    distance_kilometers: str
