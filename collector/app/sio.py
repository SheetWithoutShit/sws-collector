"""This module provides functionality for socketio interactions."""

import socketio

from app.config import JWT_SECRET_KEY
from app.utils.jwt import decode_token
from app.utils.errors import SWSTokenError


sio = socketio.AsyncServer(async_mode="aiohttp")


class TransactionEvent(socketio.AsyncNamespace):
    """Class that provides functionality to work with transaction events."""

    namespace = "/transaction"

    @classmethod
    async def on_subscribe(cls, sid, message):
        """Event handler for transaction subscribing."""
        token = message.get("token", "").split("Bearer ")[-1]
        try:
            payload = decode_token(token, JWT_SECRET_KEY)
        except SWSTokenError:
            return

        user_id = payload["user_id"]

        sio.enter_room(sid, user_id, namespace=cls.namespace)
        event_message = {"success": True}
        await sio.emit("subscribed", event_message, room=user_id, namespace=cls.namespace)

    @classmethod
    async def emit_new_transaction(cls, user_id, transaction):
        """Emit new transaction event to client."""
        # TODO: consider if we need to put whole transaction dict or simple message will be enough
        event_message = {"transaction": transaction}
        await sio.emit("new transaction", event_message, room=user_id, namespace=cls.namespace)


sio.register_namespace(TransactionEvent("/transaction"))
