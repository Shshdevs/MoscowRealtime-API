from supabase import create_client, Client
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class SupabaseStorageManager:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.bucket_name = "analyzed-images" 
    
    def get_image_by_url(self, image_path: str) -> Optional[bytes]:
        try:
            response = self.supabase.storage.from_(self.bucket_name).download(image_path)
            if response:
                return response
            else:
                return None
        except Exception as e:
            logger.error(f"Supabase download error: {e}")
            return None