"""This module provides app initialization."""

import asyncio
import logging

from aiohttp.web import Application
from core.database.postgres import PoolManager as PGPoolManager
from core.database.redis import PoolManager as RedisPoolManager

from app.views import routes


LOG = logging.getLogger("")
LOG_FORMAT = "%(asctime)s - %(levelname)s: %(name)s: %(message)s"
ACCESS_LOG_FORMAT = "%a [VIEW: %r] [RESPONSE: %s (%bb)] [TIME: %Dms]"
SELECT_MCC_CODES = """SELECT code, category FROM "MCC";"""


async def prepare_data(app):
    """
    Prepare required data for correct application work.
        * Store mcc codes retrieved from postgres to redis.
    """
    postgres, redis = app["postgres"], app["redis"]
    codes = {x["code"]: x["category"] for x in await postgres.fetch(SELECT_MCC_CODES)}
    await redis.dump("mcc", codes)
    LOG.debug("Data was successfully prepared.")

    yield

    await redis.remove("mcc")
    LOG.debug("Data was successfully cleaned.")


async def init_clients(app):
    """Initialize aiohttp application with required clients."""
    app["postgres"] = postgres = await PGPoolManager.create()
    app["redis"] = redis = await RedisPoolManager.create()
    LOG.debug("Clients has successfully initialized.")

    yield

    await asyncio.gather(
        postgres.close(),
        redis.close(),
    )
    LOG.debug("Clients has successfully closed.")


def init_app():
    """Prepare aiohttp web server for further running."""
    app = Application()

    app.add_routes(routes)

    app.cleanup_ctx.append(init_clients)
    app.cleanup_ctx.append(prepare_data)

    return app
