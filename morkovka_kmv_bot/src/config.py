import os
from dotenv import load_dotenv
from pathlib import Path

# Загрузка .env из корня проекта (на уровень выше src)
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS').split(','))) if os.getenv('ADMIN_IDS') else []

    FIREBASE_CERTIFICATE = {
        "type": os.getenv('FIREBASE_TYPE'),
        "project_id": os.getenv('FIREBASE_PROJECT_ID'),
        "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
        "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
        "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
        "client_id": os.getenv('FIREBASE_CLIENT_ID'),
        "auth_uri": os.getenv('FIREBASE_AUTH_URI'),
        "token_uri": os.getenv('FIREBASE_TOKEN_URI'),
        "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_CERT_URL'),
        "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_CERT_URL')
    }

    PRODUCT_CATEGORIES = [
        "Зелень",
        "Сезонный стол",
        "Основная витрина",
        "Холодильная горка",
        "Экзотика",
        "Ягоды",
        "Орехи/сухофрукты",
        "Бакалея",
        "Бар"
    ]

    MIN_SEARCH_QUERY_LENGTH = 3
    MAX_SEARCH_RESULTS = 10