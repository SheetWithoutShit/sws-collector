"""Module that includes functionality to work with mcc data."""

import logging

from sqlalchemy.exc import SQLAlchemyError

from app.db import db
from app.utils.errors import SWSDatabaseError


LOGGER = logging.getLogger(__name__)


SELECT_MCC_CODES = """
    SELECT code FROM "MCC";
"""


class MCC:
    """Model that provides methods to work with MCC data."""

    GET_ALL_QUERY = db.text("""
        SELECT * FROM mcc;
    """)

    @classmethod
    async def get_all(cls):
        """Retrieve all MCC instances."""
        # TODO: implement caching since it is the same all time
        try:
            mccs = await db.all(cls.GET_ALL_QUERY)
        except SQLAlchemyError as err:
            LOGGER.error("Couldn't retrieve all MCC. Error: %s", err)
            raise SWSDatabaseError("Failed to retrieve all MCC.")

        return mccs
