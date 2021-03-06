"""This module provides config variables for collector app."""

import os

from sqlalchemy.engine.url import URL

# Collector stuff
APP_MODE = os.getenv("APP_MODE", "DEV")

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(APP_DIR, os.pardir))
TEMPLATES_DIR = os.path.join(APP_DIR, "templates")
COLLECTOR_WEBHOOK_SECRET = os.environ["MONOBANK_WEBHOOK_SECRET"]

# Postgres stuff
POSTGRES_DRIVER_NAME = "postgres"
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "spentlessuser")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_DB = os.getenv("POSTGRES_DB", "spentless")
POSTGRES_POOL_MIN_SIZE = int(os.getenv("POSTGRES_POOL_MIN_SIZE", "1"))
POSTGRES_POOL_MAX_SIZE = int(os.getenv("POSTGRES_POOL_MAX_SIZE", "16"))
POSTGRES_RETRY_LIMIT = int(os.getenv("POSTGRES_RETRY_LIMIT", "32"))
POSTGRES_RETRY_INTERVAL = int(os.getenv("POSTGRES_RETRY_INTERVAL", "1"))
POSTGRES_DSN_STAGING = os.getenv("DATABASE_URL")
POSTGRES_DSN_DEV = URL(
    drivername=POSTGRES_DRIVER_NAME,
    username=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    database=POSTGRES_DB,
)

# REDIS stuff
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

# JWT stuff
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]

# Telegram stuff
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
