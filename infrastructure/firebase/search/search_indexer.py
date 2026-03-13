import logging


logger = logging.getLogger(__name__)


class SearchIndexer:
    COLLECTION_SEARCH_FIELDS = {
        "organizations": ("search_keywords",),
        "quests": ("search_prefixes",),
        "users": ("search_prefixes",),
        "locations": ("search_prefixes",),
    }

    def __init__(self, db, builder, collection_name: str = "quests"):
        self.db = db
        self.builder = builder
        self.collection_name = collection_name

    @property
    def collection(self):
        return self.db.collection(self.collection_name)

    def _build_search_payload(self, data: dict) -> dict:
        fields = self.COLLECTION_SEARCH_FIELDS.get(
            self.collection_name,
            ("search_prefixes",),
        )

        payload = {}

        if "search_keywords" in fields:
            payload["search_keywords"] = self.builder.extract_keywords(data)

        if "search_prefixes" in fields:
            payload["search_prefixes"] = self.builder.build_prefixes(data)

        return payload

    def _is_payload_up_to_date(self, data: dict, new_payload: dict) -> bool:
        for field_name, new_value in new_payload.items():
            current_value = sorted(data.get(field_name, []))
            if current_value != sorted(new_value):
                return False
        return True

    def reindex_document_snapshot(self, doc_snapshot) -> bool:
        data = doc_snapshot.to_dict() or {}
        new_payload = self._build_search_payload(data)

        if self._is_payload_up_to_date(data, new_payload):
            logger.info(
                "[SKIP] %s: search fields already up to date",
                doc_snapshot.id,
            )
            return False

        doc_snapshot.reference.update(new_payload)

        logger.info(
            "[UPDATED] %s: %s",
            doc_snapshot.id,
            {
                field_name: len(field_value)
                for field_name, field_value in new_payload.items()
            },
        )
        return True

    def reindex_document_by_id(self, doc_id: str) -> bool:
        doc_snapshot = self.collection.document(doc_id).get()

        if not doc_snapshot.exists:
            logger.warning("[SKIP] %s: document does not exist", doc_id)
            return False

        return self.reindex_document_snapshot(doc_snapshot)

    def backfill_all(self) -> None:
        for doc_snapshot in self.collection.stream():
            try:
                self.reindex_document_snapshot(doc_snapshot)
            except Exception as exc:
                logger.exception("[ERROR] %s: %s", doc_snapshot.id, exc)
