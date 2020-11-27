"""This module provides functionality for cache interactions."""

from aiocache import Cache

from app import config


MCC_CODES_CACHE_KEY = "mcc-codes"
MCC_CATEGORY_CACHE_KEY = "mcc-category--{mcc_code}"
MCC_CATEGORY_CACHE_EXPIRE = 60 * 60  # 1h

cache = Cache.from_url(config.REDIS_URL)
