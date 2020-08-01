"""Module that includes functionality to work with transaction data."""

import logging
from datetime import datetime

from asyncpg import exceptions


LOG = logging.getLogger(__name__)


INSERT_TRANSACTION = """
    INSERT INTO "TRANSACTION" (id, user_id, amount, balance, cashback, mcc, timestamp, info)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8);
"""


class Transaction:
    """Model that provides methods to work with transaction data."""

    def __init__(self, postgres=None, redis=None):
        """Initialize transaction instance with required clients."""
        self._postgres = postgres
        self._redis = redis

    async def insert_transaction(self, user_id, mcc, transaction):
        """Insert transaction element to postgres initially formatting it."""
        timestamp = datetime.fromtimestamp(transaction["timestamp"])
        query_args = [
            transaction["id"], user_id, transaction["amount"], transaction["balance"],
            transaction["cashback"], mcc, timestamp, transaction["info"],
        ]

        try:
            await self._postgres.execute(INSERT_TRANSACTION, *query_args)
        except exceptions.PostgresError as err:
            LOG.error("Could not insert transaction for user=%s: %s. Error: %s", user_id, transaction, err)
