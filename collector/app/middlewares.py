"""This module provides middlewares for collector application."""

import json
from http import HTTPStatus

from aiohttp import web


def error_middleware(error_handlers):
    """Return custom error handler."""

    @web.middleware
    async def error_middleware_inner(request, handler):
        """Handle specific http errors using custom views."""
        try:
            return await handler(request)
        except web.HTTPException as ex:
            error_handler = error_handlers.get(ex.status)
            if error_handler:
                return await error_handler(request)

            raise ex

    return error_middleware_inner


@web.middleware
async def body_validator_middleware(request, handler):
    """Check if provided body data for mutation methods is correct."""
    if request.body_exists:
        content = await request.read()
        try:
            request.body = json.loads(content)
        except json.decoder.JSONDecodeError:
            return web.json_response(
                data={"success": False, "message": "Wrong input. Can't deserialize body input."},
                status=HTTPStatus.BAD_REQUEST
            )

    return await handler(request)
