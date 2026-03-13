import logging
import os
from datetime import datetime

import cv2
import numpy as np


logger = logging.getLogger(__name__)


class ImageAnalysisService:
    def __init__(
        self,
        detector,
        storage_manager,
        history_repository,
        guide_provider,
        public_base_url: str | None = None,
    ):
        self.detector = detector
        self.storage_manager = storage_manager
        self.history_repository = history_repository
        self.guide_provider = guide_provider
        self.public_base_url = public_base_url or os.getenv("SUPABASE_URL", "")

    def compress_image(
        self,
        image_data: bytes,
        quality: int = 85,
        max_width: int = 1920,
        max_height: int = 1080,
    ) -> bytes:
        try:
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                logger.warning("Failed to decode image for compression, returning original")
                return image_data

            height, width = img.shape[:2]

            if width > max_width or height > max_height:
                scale = min(max_width / width, max_height / height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
                logger.info(
                    "Image resized from %sx%s to %sx%s",
                    width,
                    height,
                    new_width,
                    new_height,
                )

            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            success, compressed_image_data = cv2.imencode(".jpg", img, encode_param)

            if success:
                logger.info(
                    "Image compressed: original=%s bytes compressed=%s bytes",
                    len(image_data),
                    len(compressed_image_data),
                )
                return compressed_image_data.tobytes()

            logger.warning("Compression failed, returning original image")
            return image_data

        except Exception as exc:
            logger.error("Compression error: %s", exc)
            return image_data

    def _decode_image(self, image_data: bytes):
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Failed to decode image")

        return img

    def analyze(self, img_path: str, user_id: str | None = None) -> dict:
        if not self.detector.is_loaded():
            raise RuntimeError("YOLO model is not loaded")

        image_bytes = self.storage_manager.get_image_by_url(img_path)
        if image_bytes is None:
            raise ValueError("Failed to load image")

        compressed_image_data = self.compress_image(image_bytes)
        img = self._decode_image(compressed_image_data)

        detections, labels = self.detector.predict(img)

        result = {
            "success": True,
            "detections": detections,
            "total_objects": len(detections),
            "timestamp": int(datetime.now().timestamp()),
        }

        if result["total_objects"] == 0:
            return {
                "success": False,
                "error": "Unrecognized",
                "status_code": 400,
            }

        first_name = result["detections"][0].get("name")
        result["YandexGPTGuide"] = self.guide_provider(first_name)
        result["imageSavedUrl"] = (
            f"{self.public_base_url}/storage/v1/object/public/analyzed-images/{img_path}"
        )
        result["userAuthor"] = user_id
        result["labels"] = labels

        result["id"] = self.history_repository.add(result)
        logger.info("Analysis saved with id=%s", result["id"])

        return result
