from typing import Optional


class SearchIndexer:
    def __init__(self, db, builder, collection_name: str = "quests"):
        self.db = db
        self.builder = builder
        self.collection_name = collection_name

    @property
    def collection(self):
        return self.db.collection(self.collection_name)

    def reindex_document_snapshot(self, doc_snapshot) -> bool:
        data = doc_snapshot.to_dict() or {}
        new_payload = self.builder.build_search_payload(data)

        current_keywords = sorted(data.get("search_keywords", []))
        current_prefixes = sorted(data.get("search_prefixes", []))

        if (
            current_keywords == new_payload["search_keywords"]
            and current_prefixes == new_payload["search_prefixes"]
        ):
            print(f"[SKIP] {doc_snapshot.id}: search fields already up to date")
            return False

        doc_snapshot.reference.update(new_payload)
        print(
            f"[UPDATED] {doc_snapshot.id}: "
            f"{len(new_payload['search_keywords'])} keywords, "
            f"{len(new_payload['search_prefixes'])} prefixes"
        )
        return True

    def reindex_document_by_id(self, doc_id: str) -> bool:
        doc_snapshot = self.collection.document(doc_id).get()

        if not doc_snapshot.exists:
            print(f"[SKIP] {doc_id}: document does not exist")
            return False

        return self.reindex_document_snapshot(doc_snapshot)

    def backfill_all(self) -> None:
        for doc_snapshot in self.collection.stream():
            try:
                self.reindex_document_snapshot(doc_snapshot)
            except Exception as exc:
                print(f"[ERROR] {doc_snapshot.id}: {exc}")