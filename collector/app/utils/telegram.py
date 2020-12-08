"""This module provides functionality for pushing notification event to SQS."""

import logging

from app.config import TELEGRAM_API


LOGGER = logging.getLogger(__name__)

TELEGRAM_API_SEND_MESSAGE = f"{TELEGRAM_API}/sendMessage"


async def send_notification(aio_session, telegram_id, text, parse_mode="markdown", disable_notification=True):
    """Send notification message to appropriated user."""
    notification_params = {
        "chat_id": telegram_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_notification": str(disable_notification).lower()
    }

    async with aio_session.get(TELEGRAM_API_SEND_MESSAGE, params=notification_params) as response:
        response_json = await response.json()
        if not response_json["ok"]:
            LOGGER.error("A telegram notification was not delivered. Response: %s", response_json)
