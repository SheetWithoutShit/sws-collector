"""This module provides app initialization."""

import logging

from aiohttp.web import Application
from aiojobs.aiohttp import setup as aiojobs_setup

from core.database.redis import PoolManager as RedisPoolManager

from app import config
from app.db import db
from app.sio import sio
from app.api.monobank import monobank_routes
from app.api.index import handle_404, handle_405, handle_500, internal_routes
from app.middlewares import body_validator_middleware, error_middleware, auth_middleware


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


# TODO: for testing purposes, remove it when ui part will be ready
async def index(request):
    d = """
    <html>
    <head>
        <script type="text/javascript" src="//code.jquery.com/jquery-2.1.4.min.js"></script>
        <script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/socket.io/1.3.5/socket.io.min.js"></script>
        <script type="text/javascript"">
            $(document).ready(function(){
                namespace = '/transaction';
                var token = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1OTkwMzgzMjYsImV4cCI6MTU5OTY0MzEyNiwidXNlcl9pZCI6NX0.ZAGU9ogJQTgy7TgzpqlE25TB4rwvxnL55jnmPOSyWPE"
                const socket = io.connect('localhost:5010/transaction');
                socket.on('new transaction', function(msg) {
                    console.log(msg)
                    $('#log').append('<br>Received: ' + msg);
                });
                socket.on('connect', function() {
                    socket.emit('subscribe', {token: token});
                });
                socket.on('subscribed', function(msg) {
                    $('#log').append('<br>Received 1: ' + msg);
                });
            });
        </script>
    </head>
    <body>
        LOG
        <div><p id="log"></p></div>
    </body>
    </html>
    """
    from aiohttp import web
    return web.Response(text=d, content_type='text/html')


def init_app():
    """Prepare aiohttp web server for further running."""
    app = Application()

    sio.attach(app)
    aiojobs_setup(app)
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
    app.router.add_route("GET", "/index", index)

    app.cleanup_ctx.append(init_clients)
    app.on_startup.append(init_config)

    app.middlewares.append(auth_middleware)
    app.middlewares.append(body_validator_middleware)
    app.middlewares.append(error_middleware({
        404: handle_404,
        405: handle_405,
        500: handle_500
    }))

    return app
