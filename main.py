import logging
import signal

from waitress import serve

from config import Config
from shared.logging import setup_logging
from presentation.api.app import create_app
from infrastructure.firebase.firebase_client import get_firestore_client
from infrastructure.firebase.search.search_prefix_builder import SearchPrefixBuilder
from infrastructure.firebase.search.search_indexer import SearchIndexer
from infrastructure.firebase.listeners.collection_listener import CollectionListener


setup_logging()
logger = logging.getLogger(__name__)


def start_listeners():
    db = get_firestore_client()
    builder = SearchPrefixBuilder()

    collection_names = ["quests", "users", "locations"]
    listeners = []

    for collection_name in collection_names:
        logger.info("Starting listener for collection: %s", collection_name)

        indexer = SearchIndexer(
            db=db,
            builder=builder,
            collection_name=collection_name,
        )

        listener = CollectionListener(indexer=indexer)
        listener.start()
        listeners.append(listener)

    logger.info("Started %s listeners", len(listeners))
    return listeners

def main():

    logger.info("Starting application")

    listeners = start_listeners()

    app = create_app()

    def shutdown_handler(signum, frame):

        logger.info("Shutdown signal received")

        try:
            for listener in listeners:
                listener.stop()
        except Exception:
            pass

        raise SystemExit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    logger.info(
        "Starting HTTP server on %s:%s",
        Config.HOST,
        Config.PORT,
    )

    serve(
        app,
        host=Config.HOST,
        port=Config.PORT,
        threads=Config.WAITRESS_THREADS,
        url_prefix="/api",
    )

if __name__ == "__main__":
    main()