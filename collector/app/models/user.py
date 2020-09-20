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
    SELECT_LIMIT = db.text("""
        SELECT mcc_category.id as category_id,
            mcc_category.name as category_name,
            budget_limit.amount
        FROM mcc
        LEFT JOIN "mcc_category" on mcc.category_id=mcc_category.id
        LEFT JOIN "limit" as budget_limit on mcc_category.id=budget_limit.category_id
        WHERE budget_limit.user_id = :user_id and mcc.code = :mcc_code
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

    @classmethod
    async def get_limit(cls, user_id, mcc_code):
        """Return queried user`s limit by provided mcc code."""
        try:
            limit = await db.one(cls.SELECT_LIMIT, user_id=user_id, mcc_code=mcc_code)
        except exceptions.NoResultFound:
            LOGGER.error("Could not find limit by mcc code=%s for user=%s.", mcc_code, user_id)
            raise SWSDatabaseError
        except SQLAlchemyError as err:
            LOGGER.error("Failed to fetch limit by mcc code=% for user=%s. Error: %s", mcc_code, user_id, err)
            raise SWSDatabaseError

        return limit
