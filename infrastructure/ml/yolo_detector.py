import json
import logging


logger = logging.getLogger(__name__)


class YOLODetector:
    def __init__(self, model_path: str = "sensitive/best.pt", locations_path: str = "sensitive/locations.json"):
        self.model_path = model_path
        self.locations_path = locations_path
        self.model = None
        self.load_model()

    def load_model(self):
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.model_path)
            logger.info("YOLO model loaded successfully")
        except ImportError as exc:
            logger.error("Failed to import ultralytics: %s", exc)
            logger.info("Install dependency: pip install ultralytics")
            self.model = None
        except Exception as exc:
            logger.error("Failed to load YOLO model: %s", exc)
            self.model = None

    def is_loaded(self) -> bool:
        return self.model is not None

    def find_location_id_name(self, class_label: str):
        with open(self.locations_path, "r", encoding="utf-8") as f:
            locations = json.load(f)

        for location in locations:
            label = location.get("label")
            if isinstance(label, str) and label.lower() == class_label.lower():
                return location.get("id"), location.get("name")

        return None, None

    def predict(self, image_np):
        if self.model is None:
            raise ValueError("YOLO model is not loaded")

        try:
            results = self.model(image_np)
            detections = []

            for result in results:
                for box in result.boxes:
                    class_name = self.model.names[int(box.cls)]
                    confidence = float(box.conf)

                    if confidence > 0.7 and "Other" not in class_name and "Peoples" not in class_name:
                        location_id, name = self.find_location_id_name(class_name)
                        if location_id is not None and name is not None:
                            detections.append({
                                "locationId": location_id,
                                "name": name,
                                "confidence": confidence,
                            })

            detections.sort(key=lambda x: x["confidence"], reverse=True)

            return detections

        except Exception as exc:
            logger.error("YOLO prediction error: %s", exc)
            raise