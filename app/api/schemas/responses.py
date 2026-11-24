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
