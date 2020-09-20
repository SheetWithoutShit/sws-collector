"""Module that includes functionality to work with transaction data."""

import logging
from datetime import datetime

from asyncpg import exceptions
from sqlalchemy.exc import SQLAlchemyError

from app.db import db
from app.utils.errors import SWSDatabaseError


LOGGER = logging.getLogger(__name__)


class Transaction:
    """Class that provides methods to work with Transaction data."""

    CREATE_QUERY = db.text("""
        INSERT INTO transaction (id, user_id, amount, balance, cashback, mcc, timestamp, info)
        VALUES (:id, :user_id, :amount, :balance, :cashback, :mcc, :timestamp, :info);
    """)

    @classmethod
    async def create_transaction(cls, user_id, mcc, transaction):
        """Insert transaction element to postgres initially formatting it."""
        timestamp = datetime.fromtimestamp(transaction["timestamp"])
        try:
            return await db.status(
                cls.CREATE_QUERY,
                id=transaction["id"],
                user_id=user_id,
                amount=transaction["amount"],
                balance=transaction["balance"],
                cashback=transaction["cashback"],
                mcc=mcc,
                timestamp=timestamp,
                info=transaction["info"]
            )
        except exceptions.UniqueViolationError:
            LOGGER.error("The transaction already exists. Transaction: %s", transaction)
            raise SWSDatabaseError(f"Failure. The transaction={transaction['id']} already exists.")
        except SQLAlchemyError as err:
            LOGGER.error("Could not create transaction for user=%s: %s. Error: %s", user_id, transaction, err)
            raise SWSDatabaseError("Failure. Failed to create transaction.")
