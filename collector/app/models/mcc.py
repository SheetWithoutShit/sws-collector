"""Module that includes functionality to work with mcc data."""

import logging

from sqlalchemy.exc import SQLAlchemyError

from app.db import db
from app.cache import cache, MCC_CODES_CACHE_KEY
from app.utils.errors import SWSDatabaseError


LOGGER = logging.getLogger(__name__)


class MCC:
    """Class that provides methods to work with MCC data."""

    GET_CODES_QUERY = db.text("""
        SELECT code FROM mcc;
    """)

    @classmethod
    async def get_codes(cls):
        """Retrieve all MCC codes."""
        mcc_codes = await cache.get(MCC_CODES_CACHE_KEY)
        if mcc_codes:
            return mcc_codes
        try:
            mcc_codes = [mcc.code for mcc in await db.all(cls.GET_CODES_QUERY)]
        except SQLAlchemyError as err:
            LOGGER.error("Couldn't retrieve all MCC codes. Error: %s", err)
            raise SWSDatabaseError("Failure. Failed to retrieve all MCC codes.")
        else:
            await cache.set(MCC_CODES_CACHE_KEY, mcc_codes)

        return mcc_codes
