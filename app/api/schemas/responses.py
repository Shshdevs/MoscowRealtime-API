from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    success: bool = False
    error: str


class DetectionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    location_id: str = Field(alias="locationId")
    name: str
    confidence: float


class ClosestLocationResponse(BaseModel):
    success: bool = True
    closest_location: dict
    distance: str


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str


class EventDateResponse(BaseModel):
    start: int
    end: int


class EventVenueResponse(BaseModel):
    city: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class EventResponse(BaseModel):
    id: int
    title: str
    description: str
    body_text: str
    dates: list[EventDateResponse]
    categories: list[str]
    age_restriction: str | None = None
    price_min: float | None = None
    price_max: float | None = None
    is_free: bool
    image_url: str | None = None
    site_url: str
    venue: EventVenueResponse | None = None


class EventsResponse(BaseModel):
    success: bool = True
    total: int
    events: list[EventResponse]


class EventDetailResponse(BaseModel):
    success: bool = True
    event: EventResponse
