from supabase import create_client, Client
from typing import Optional
import logging
import time

logger = logging.getLogger(__name__)

class SupabaseStorageManager:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.bucket_name = "analyzed-images" 
    
    def get_image_by_url(self, image_path: str, retries: int = 3, backoff: float = 1.5,) -> Optional[bytes]:
        for attempt in range(retries):
            try:
                file_bytes = self.supabase.storage.from_(self.bucket_name).download(image_path)

                if file_bytes:
                    return file_bytes

                logger.warning("Empty response: %s", image_path)

            except Exception as e:
                logger.warning(
                    "Download attempt %d failed: path=%s error=%s",
                    attempt + 1,
                    image_path,
                    e
                )

            sleep_time = backoff ** attempt
            time.sleep(sleep_time)

        logger.error("Failed to download after %d attempts: %s", retries, image_path)
        return None
