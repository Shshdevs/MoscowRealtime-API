class FirestoreLocationRepository:
    def __init__(self, db, collection_name: str = "locations"):
        self.db = db
        self.collection_name = collection_name

    def get_all(self) -> list:
        docs = self.db.collection(self.collection_name).stream()
        return [doc.to_dict() for doc in docs]
