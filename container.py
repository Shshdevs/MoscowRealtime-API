import os

from application.services.image_analysis_service import ImageAnalysisService
from application.services.location_service import LocationService
from infrastructure.firebase.discovery_repository import FirestoreDiscoveryRepository
from infrastructure.firebase.firebase_client import get_firestore_client
from infrastructure.firebase.location_repository import FirestoreLocationRepository
from infrastructure.ml.yolo_detector import YOLODetector
from infrastructure.yandex_gpt.yandex_guide import runYandexGPT
from infrastructure.supabase.supabase_manager import SupabaseStorageManager


def build_container():
    db = get_firestore_client()

    location_repository = FirestoreLocationRepository(db)
    discovery_repository = FirestoreDiscoveryRepository(db)

    detector = YOLODetector()

    storage_manager = SupabaseStorageManager(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY"),
    )

    image_analysis_service = ImageAnalysisService(
        detector=detector,
        storage_manager=storage_manager,
        history_repository=discovery_repository,
        guide_provider=runYandexGPT,
        public_base_url=os.getenv("SUPABASE_URL"),
    )

    return {
        "db": db,
        "location_repository": location_repository,
        "discovery_repository": discovery_repository,
        "location_service": LocationService(location_repository),
        "detector": detector,
        "storage_manager": storage_manager,
        "image_analysis_service": image_analysis_service,
    }
