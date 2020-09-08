"""This module provides functionality for cache interactions."""

from aiocache import Cache

from app.config import REDIS_HOST, REDIS_PORT


MCC_CODES_CACHE_KEY = "mcc-codes"

cache = Cache(Cache.REDIS, endpoint=REDIS_HOST, port=REDIS_PORT)
