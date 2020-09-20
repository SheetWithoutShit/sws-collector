"""Module that includes functionality to work with user data."""

import logging

from gino import exceptions
from sqlalchemy.exc import SQLAlchemyError

from app.db import db
from app.utils.errors import SWSDatabaseError


LOGGER = logging.getLogger(__name__)


class User:
    """Class that provides methods to work with User data."""

    SELECT_USER = db.text("""
        SELECT *
        FROM "user"
        WHERE id = :user_id
    """)

    @classmethod
    async def get(cls, user_id):
        """Return queried user record by provided id."""
        try:
            user = await db.one(cls.SELECT_USER, user_id=user_id)
        except exceptions.NoResultFound:
            LOGGER.error("Could not find user=%s.", user_id)
            raise SWSDatabaseError
        except SQLAlchemyError as err:
            LOGGER.error("Failed to fetch user=%s. Error: %s", user_id, err)
            raise SWSDatabaseError

        return user
