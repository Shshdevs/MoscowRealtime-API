from geopy.distance import geodesic


class LocationService:
    def __init__(self, location_repository):
        self.location_repository = location_repository

    def get_closest(self, lat: float, lon: float) -> dict:
        locations = self.location_repository.get_all()
        if not locations:
            return {"error": "No locations found in Firestore"}

        user_coords = (lat, lon)
        closest_location = None
        min_distance = float("inf")

        for location in locations:
            loc_coords = (location["lat"], location["lon"])
            distance = geodesic(user_coords, loc_coords).kilometers

            if distance < min_distance:
                min_distance = distance
                closest_location = location

        return {
            "closest_loc": closest_location,
            "distance": f"{min_distance:.2f}",
        }
