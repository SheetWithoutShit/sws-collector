"""Module that includes functionality to work with mcc data."""

import logging

from gino import exceptions
from sqlalchemy.exc import SQLAlchemyError

from app.db import db
from app.cache import cache, MCC_CODES_CACHE_KEY, MCC_CATEGORY_CACHE_KEY, MCC_CATEGORY_CACHE_EXPIRE
from app.utils.errors import SWSDatabaseError


LOGGER = logging.getLogger(__name__)


class MCC:
    """Class that provides methods to work with MCC data."""

    OTHER_CATEGORY = "Other"
    SELECT_CODES = db.text("""
        SELECT code FROM mcc;
    """)
    SELECT_CATEGORY = db.text("""
        SELECT name
        FROM mcc
        JOIN mcc_category on category_id=id
        WHERE code=:mcc_code
    """)

    @classmethod
    async def get_codes(cls):
        """Retrieve all MCC codes."""
        mcc_codes = await cache.get(MCC_CODES_CACHE_KEY)
        if mcc_codes:
            return mcc_codes
        try:
            mcc_codes = [mcc.code for mcc in await db.all(cls.SELECT_CODES)]
        except SQLAlchemyError as err:
            LOGGER.error("Could not retrieve all MCC codes. Error: %s", err)
            raise SWSDatabaseError("Failure. Failed to retrieve all MCC codes.")
        else:
            await cache.set(MCC_CODES_CACHE_KEY, mcc_codes)

        return mcc_codes

    @classmethod
    async def get_category(cls, mcc_code):
        """Retrieve MCC category by provided id."""
        mcc_category_key = MCC_CATEGORY_CACHE_KEY.format(mcc_code=mcc_code)
        mcc_category = await cache.get(mcc_category_key)
        if mcc_category:
            return mcc_category
        try:
            mcc_category = await db.one(cls.SELECT_CATEGORY, mcc_code=mcc_code)
        except exceptions.NoResultFound:
            LOGGER.error("Could not find category for mcc code=%s.", mcc_code)
            return cls.OTHER_CATEGORY
        except SQLAlchemyError as err:
            LOGGER.error("Could not retrieve all MCC category for code=%s. Error: %s", mcc_code, err)
            raise SWSDatabaseError(f"Failure. Failed to retrieve MCC category for code={mcc_code}.")
        else:
            await cache.set(mcc_category_key, mcc_category.name, MCC_CATEGORY_CACHE_EXPIRE)

        return mcc_category.name
