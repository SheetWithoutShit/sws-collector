"""This module provides app initialization."""

import os
import logging

from aiohttp.web import Application
from aiojobs.aiohttp import setup as aiojobs_setup

from app import config
from app.db import db, get_database_dsn
from app.sio import sio
from app.middlewares import body_validator_middleware, error_middleware
from app.api.monobank import monobank_routes
from app.api.index import handle_404, handle_405, handle_500, internal_routes


LOGGER = logging.getLogger(__name__)
LOG_FORMAT = "%(asctime)s - %(levelname)s: %(name)s: %(message)s"


def init_logging():
    """
    Initialize logging stream with info level to console and
    create file logger with info level if permission to file allowed.
    """
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)

    # disabling gino postgres echo logs
    # in order to set echo pass echo=True to db config dict
    logging.getLogger("gino.engine._SAEngine").propagate = False

    log_dir = os.getenv("LOG_DIR")
    log_filepath = f'{log_dir}/collector.log'
    if log_dir and os.path.isdir(log_filepath) and os.access(log_dir, os.W_OK):
        formatter = logging.Formatter(LOG_FORMAT)
        file_handler = logging.FileHandler(log_filepath)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logging.getLogger("").addHandler(file_handler)


async def init_config(app):
    """Initialize aiohttp application with required constants."""
    setattr(app, "config", config)
    LOGGER.debug("Application config has successfully set up.")


def init_db(app):
    """Initialize database postgres connection based on server mode."""
    db.init_app(
        app,
        dict(
            dsn=get_database_dsn(),
            min_size=config.POSTGRES_POOL_MIN_SIZE,
            max_size=config.POSTGRES_POOL_MAX_SIZE,
            retry_limit=config.POSTGRES_RETRY_LIMIT,
            retry_interval=config.POSTGRES_RETRY_INTERVAL
        ),
    )


# TODO: for testing purposes, remove it when ui part will be ready
# async def index(request):
#     """For testing purposes"""
#     index = """
#     <html>
#     <head>
#         <script type="text/javascript" src="//code.jquery.com/jquery-2.1.4.min.js"></script>
#         <script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/socket.io/1.3.5/socket.io.min.js">
#         </script>
#         <script type="text/javascript"">
#             $(document).ready(function(){
#                 namespace = '/transaction';
#                 var token = "test"
#                 const socket = io.connect('localhost:5010/transaction');
#                 socket.on('new transaction', function(msg) {
#                     console.log(msg)
#                     $('#log').append('<br>Received: ' + msg);
#                 });
#                 socket.on('connect', function() {
#                     socket.emit('subscribe', {token: token});
#                 });
#                 socket.on('subscribed', function(msg) {
#                     $('#log').append('<br>Received 1: ' + msg);
#                 });
#             });
#         </script>
#     </head>
#     <body>
#         LOG
#         <div><p id="log"></p></div>
#     </body>
#     </html>
#     """
#     return Response(text=index, content_type='text/html')


def init_app():
    """Prepare aiohttp web server for further running."""
    app = Application()

    init_logging()
    init_db(app)

    sio.attach(app)
    aiojobs_setup(app)

    app.add_routes(monobank_routes)
    app.add_routes(internal_routes)

    app.on_startup.append(init_config)

    app.middlewares.append(db)
    app.middlewares.append(body_validator_middleware)
    app.middlewares.append(error_middleware({
        404: handle_404,
        405: handle_405,
        500: handle_500
    }))

    return app
