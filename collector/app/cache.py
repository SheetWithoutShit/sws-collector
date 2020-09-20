"""This module provides functionality for cache interactions."""

from aiocache import Cache

from app.config import REDIS_HOST, REDIS_PORT


MCC_CODES_CACHE_KEY = "mcc-codes"
MCC_CATEGORY_CACHE_KEY = "mcc-category--{mcc_code}"
MCC_CATEGORY_CACHE_EXPIRE = 60 * 60  # 1h

cache = Cache(Cache.REDIS, endpoint=REDIS_HOST, port=REDIS_PORT)
