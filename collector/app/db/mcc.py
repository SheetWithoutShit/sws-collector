"""Module that includes functionality to work with mcc data."""

import logging

from asyncpg import exceptions


LOGGER = logging.getLogger(__name__)


SELECT_MCC_CODES = """
    SELECT code FROM "MCC";
"""


class MCC:
    """Model that provides methods to work with mcc data."""

    MCC_CACHE_KEY = "MCC_CODES"

    def __init__(self, postgres=None, redis=None):
        """Initialize mcc instance with required clients."""
        self._postgres = postgres
        self._redis = redis

    async def get_mcc_codes(self):
        """Return True if mcc code exists."""
        mcc_codes = await self._redis.get(self.MCC_CACHE_KEY, deserialize=True, default=[])
        if mcc_codes:
            return mcc_codes

        try:
            mcc_codes = [mcc["code"] for mcc in await self._postgres.fetch(SELECT_MCC_CODES)]
        except exceptions.PostgresError as err:
            LOGGER.error("Could not check if mcc exists. Error: %s", err)

        await self._redis.dump(self.MCC_CACHE_KEY, mcc_codes)
        return mcc_codes
