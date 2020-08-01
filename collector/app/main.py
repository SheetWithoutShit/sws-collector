"""This module provides app initialization."""

import os
import asyncio
import logging

from aiohttp.web import Application
from core.database.postgres import PoolManager as PGPoolManager
from core.database.redis import PoolManager as RedisPoolManager

from app.views import routes
from app.db.transaction import Transaction
from app.db.mcc import MCC


LOG = logging.getLogger("")
LOG_FORMAT = "%(asctime)s - %(levelname)s: %(name)s: %(message)s"
ACCESS_LOG_FORMAT = "%a [VIEW: %r] [RESPONSE: %s (%bb)] [TIME: %Dms]"


async def init_clients(app):
    """Initialize aiohttp application with required clients."""
    app["postgres"] = postgres = await PGPoolManager.create()
    app["redis"] = redis = await RedisPoolManager.create()
    app["transaction"] = Transaction(postgres=postgres)
    app["mcc"] = MCC(postgres=postgres, redis=redis)
    LOG.debug("Clients has successfully initialized.")

    yield

    await asyncio.gather(
        postgres.close(),
        redis.close()
    )
    LOG.debug("Clients has successfully closed.")


async def init_constants(app):
    """Initialize aiohttp application with required constants."""
    app["constants"] = constants = {}

    constants["MONOBANK_WEBHOOK_SECRET"] = os.environ["MONOBANK_WEBHOOK_SECRET"]


def init_app():
    """Prepare aiohttp web server for further running."""
    app = Application()

    app.add_routes(routes)

    app.cleanup_ctx.append(init_clients)
    app.on_startup.append(init_constants)

    return app
