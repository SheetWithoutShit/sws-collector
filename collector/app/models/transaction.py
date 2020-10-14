"""Module that includes functionality to work with transaction data."""

import logging
from datetime import datetime

from asyncpg import exceptions
from sqlalchemy.exc import SQLAlchemyError

from app.db import db
from app.utils.errors import DatabaseError


LOGGER = logging.getLogger(__name__)


class Transaction:
    """Class that provides methods to work with Transaction data."""

    CREATE_TRANSACTION = db.text("""
        INSERT INTO transaction (id, user_id, amount, balance, cashback, mcc, timestamp, info)
        VALUES (:id, :user_id, :amount, :balance, :cashback, :mcc, :timestamp, :info);
    """)
    SELECT_CATEGORY_TRANSACTIONS_AMOUNT = db.text("""
        SELECT abs(sum(amount))
        FROM transaction
        JOIN mcc on transaction.mcc=mcc.code
        JOIN mcc_category on mcc.category_id=mcc_category.id
        WHERE timestamp between :start_date and :end_date
            and transaction.user_id = :user_id
            and mcc.category_id= :category_id
            and amount < 0
    """)

    @classmethod
    async def create_transaction(cls, user_id, mcc, transaction):
        """Insert transaction element to postgres initially formatting it."""
        timestamp = datetime.fromtimestamp(transaction["timestamp"])
        try:
            return await db.status(
                cls.CREATE_TRANSACTION,
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
            raise DatabaseError(f"Failure. The transaction={transaction['id']} already exists.")
        except SQLAlchemyError as err:
            LOGGER.error("Could not create transaction for user=%s: %s. Error: %s", user_id, transaction, err)
            raise DatabaseError("Failure. Failed to create transaction.")

    @classmethod
    async def get_category_transactions_amount(cls, user_id, category_id, start_date, end_date):
        """Retrieve category transaction amount for provided period of time."""
        try:
            amount = await db.scalar(
                cls.SELECT_CATEGORY_TRANSACTIONS_AMOUNT,
                user_id=user_id,
                category_id=category_id,
                start_date=start_date,
                end_date=end_date
            )
        except SQLAlchemyError as err:
            LOGGER.error("Could not retrieve category=%s transaction amount. Error: %s", category_id, err)
            raise DatabaseError(f"Failure. Failed to retrieve category={category_id} transaction amount.")

        return amount
