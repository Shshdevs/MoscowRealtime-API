import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    app_name: str
    host: str
    port: int
    cors_allowed_origins: tuple[str, ...]
    forwarded_allow_ips: str
    supabase_url: str
    supabase_key: str
    firebase_credentials_path: str
    yolo_model_path: str
    locations_file: str
    yandex_api_key: str | None
    yandex_folder: str | None
    yandex_model: str | None

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        return cls(
            app_name="Moscow Realtime API",
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "80")),
            cors_allowed_origins=tuple(
                origin.strip()
                for origin in os.getenv("CORS_ALLOWED_ORIGINS", "*").split(",")
                if origin.strip()
            ),
            forwarded_allow_ips=os.getenv("FORWARDED_ALLOW_IPS", "*"),
            supabase_url=os.getenv("SUPABASE_URL", ""),
            supabase_key=os.getenv("SUPABASE_KEY", ""),
            firebase_credentials_path=os.getenv(
                "FIREBASE_CREDENTIALS_PATH", "sensitive/serviceAccountKey.json"
            ),
            yolo_model_path=os.getenv("YOLO_MODEL_PATH", "sensitive/best.pt"),
            locations_file=os.getenv("LOCATIONS_FILE", "sensitive/locations.json"),
            yandex_api_key=os.getenv("YANDEX_CLOUD_API_KEY")
            or os.getenv("YANDEX_AUTH"),
            yandex_folder=os.getenv("YANDEX_CLOUD_FOLDER"),
            yandex_model=os.getenv("YANDEX_CLOUD_MODEL"),
        )
