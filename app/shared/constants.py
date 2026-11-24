FIRESTORE_COLLECTIONS = ("quests", "users", "locations", "organizations")
SEARCH_TEXT_FIELDS = (
    "description_en",
    "description_ru",
    "title_en",
    "title_ru",
    "label_en",
    "label_ru",
    "username",
    "name",
)
SEARCH_TAG_FIELDS = ("tags_en", "tags_ru")
SEARCH_FIELDS_BY_COLLECTION = {
    "organizations": ("search_keywords",),
    "quests": ("search_prefixes",),
    "users": ("search_prefixes",),
    "locations": ("search_prefixes",),
}
ANALYZED_IMAGES_BUCKET = "analyzed-images"
IMAGE_ANALYSIS_MAX_WIDTH = 1920
IMAGE_ANALYSIS_MAX_HEIGHT = 1080
IMAGE_ANALYSIS_JPEG_QUALITY = 85
