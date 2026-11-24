class FirestoreDiscoveryRepository:
    def __init__(self, db, collection_name: str = "discoveries"):
        self.db = db
        self.collection_name = collection_name

    def add(self, data: dict) -> str:
        new_doc_ref = self.db.collection(self.collection_name).add(data)
        doc_id = new_doc_ref[1].id
        self.db.collection(self.collection_name).document(doc_id).update({"id": doc_id})
        return doc_id
