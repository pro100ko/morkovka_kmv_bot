from firebase_db import FirebaseDB
from config import Config


def search_products(query):
    if len(query) < Config.MIN_SEARCH_QUERY_LENGTH:
        return []

    return FirebaseDB.search_products(query)[:Config.MAX_SEARCH_RESULTS]