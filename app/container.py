from functools import partial
from typing import TypedDict

from firebase_admin import firestore

from app.application.services.image_analysis_service import ImageAnalysisService
from app.application.services.location_service import LocationService
from app.infrastructure.firebase.discovery_repository import FirestoreDiscoveryRepository
from app.infrastructure.firebase.firebase_client import get_firestore_client
from app.infrastructure.firebase.location_repository import FirestoreLocationRepository
from app.infrastructure.ml.yolo_detector import YOLODetector
from app.infrastructure.yandex_gpt.yandex_guide import runYandexGPT
from app.infrastructure.supabase.supabase_manager import SupabaseStorageManager
from app.shared.config import Settings


class ApplicationContainer(TypedDict):
    db: firestore.Client
    location_repository: FirestoreLocationRepository
    discovery_repository: FirestoreDiscoveryRepository
    location_service: LocationService
    detector: YOLODetector
    storage_manager: SupabaseStorageManager
    image_analysis_service: ImageAnalysisService


def build_container(settings: Settings) -> ApplicationContainer:
    db = get_firestore_client(settings)

    location_repository = FirestoreLocationRepository(db)
    discovery_repository = FirestoreDiscoveryRepository(db)

    detector = YOLODetector(
        model_path=settings.yolo_model_path,
        locations_path=settings.locations_file,
    )

    if not settings.supabase_url or not settings.supabase_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set")

    if not settings.yandex_folder or not settings.yandex_model:
        raise RuntimeError("YANDEX_CLOUD_FOLDER and YANDEX_CLOUD_MODEL must be set")
    if not settings.yandex_api_key:
        raise RuntimeError("YANDEX_CLOUD_API_KEY or YANDEX_AUTH must be set")

    storage_manager = SupabaseStorageManager(
        settings.supabase_url,
        settings.supabase_key,
    )

    image_analysis_service = ImageAnalysisService(
        detector=detector,
        storage_manager=storage_manager,
        history_repository=discovery_repository,
        guide_provider=partial(
            runYandexGPT,
            api_key=settings.yandex_api_key,
            folder_id=settings.yandex_folder,
            model=settings.yandex_model,
        ),
        public_base_url=settings.supabase_url,
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
