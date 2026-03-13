import os


class Config:

    APP_NAME = "Moscow Realtime API"

    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 80))

    MAX_CONTENT_LENGTH = 50 * 1024 * 1024

    WAITRESS_THREADS = int(os.getenv("WAITRESS_THREADS", 4))

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "sensitive/best.pt")

    LOCATIONS_FILE = os.getenv("LOCATIONS_FILE", "sensitive/locations.json")
