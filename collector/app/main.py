"""This module provides app initialization."""

import logging

from aiohttp.web import Application

from core.database.redis import PoolManager as RedisPoolManager

from app import config
from app.db import db
from app.api.monobank import monobank_routes
from app.api.index import handle_404, handle_405, handle_500, internal_routes
from app.middlewares import body_validator_middleware, error_middleware


LOGGER = logging.getLogger("")


async def init_config(app):
    """Initialize aiohttp application with required constants."""
    setattr(app, "config", config)
    LOGGER.debug("Application config has successfully set up.")


async def init_clients(app):
    """Initialize aiohttp application with clients."""
    app["redis"] = redis = await RedisPoolManager.create()
    LOGGER.debug("Clients has successfully initialized.")

    yield

    await redis.close()
    LOGGER.debug("Clients has successfully closed.")


def init_app():
    """Prepare aiohttp web server for further running."""
    app = Application()

    db.init_app(
        app,
        dict(
            dsn=config.POSTGRES_DSN,
            min_size=config.POSTGRES_POOL_MIN_SIZE,
            max_size=config.POSTGRES_RETRY_INTERVAL,
            retry_limit=config.POSTGRES_RETRY_LIMIT,
            retry_interval=config.POSTGRES_RETRY_INTERVAL,
        ),
    )

    app.add_routes(monobank_routes)
    app.add_routes(internal_routes)

    app.cleanup_ctx.append(init_clients)
    app.on_startup.append(init_config)

    app.middlewares.append(body_validator_middleware)
    app.middlewares.append(error_middleware({
        404: handle_404,
        405: handle_405,
        500: handle_500
    }))

    return app
