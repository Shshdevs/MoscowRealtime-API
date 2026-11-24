from dataclasses import dataclass


@dataclass(frozen=True)
class Detection:
    location_id: str
    name: str
    confidence: float

    def to_api_dict(self) -> dict:
        return {
            "locationId": self.location_id,
            "name": self.name,
            "confidence": self.confidence,
        }
