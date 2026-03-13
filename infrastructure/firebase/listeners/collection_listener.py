import logging

logger = logging.getLogger(__name__)


class CollectionListener:
    def __init__(self, indexer):
        self.indexer = indexer
        self._watch = None
        self._initialized = False

    def _handle_snapshot(self, col_snapshot, changes, read_time):
        if not self._initialized:
            self._initialized = True
            logger.info("Initial snapshot received")
            return

        for change in changes:
            try:
                change_type = change.type.name
                doc_snapshot = change.document

                if change_type in ("ADDED", "MODIFIED"):
                    logger.info("Reindex %s: %s", change_type, doc_snapshot.id)
                    self.indexer.reindex_document_snapshot(doc_snapshot)

            except Exception as exc:
                doc_id = getattr(change.document, "id", "unknown")
                logger.exception("Listener error for %s: %s", doc_id, exc)

    def start(self):
        if self._watch is not None:
            logger.info("Listener already started")
            return

        self._watch = self.indexer.collection.on_snapshot(self._handle_snapshot)
        logger.info("Watching collection: %s", self.indexer.collection_name)

    def stop(self):
        if self._watch is not None:
            self._watch.unsubscribe()
            self._watch = None
            logger.info("Listener stopped")
