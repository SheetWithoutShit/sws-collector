"""This module provides functionality for pushing notification event to SQS."""

import asyncio
import json
import logging
from datetime import datetime

import aioboto3

from app import config
from app.models.user import User
from app.models.mcc import MCC
from app.utils.errors import SWSDatabaseError


LOGGER = logging.getLogger(__name__)
TRANSACTION_NOTIFICATION_TEXT = \
    "Transaction! 💲\n\n" \
    "▪️ Amount: *{amount}*\n" \
    "▪️ Category: *{category}*\n" \
    "▪️ Info: *{info}*\n" \
    "▪️ Balance: *{balance}*\n" \
    "▪ Timestamp: *{date}*"


async def get_transaction_event(telegram_id, transaction):
    """Push notification about a new transaction to SQS for user."""
    try:
        category = await MCC.get_category(transaction["mcc"])
    except SWSDatabaseError:
        category = "-"

    date = datetime.fromtimestamp(transaction["timestamp"]).strftime("%d.%m.%Y %H:%M:%S")
    text = TRANSACTION_NOTIFICATION_TEXT.format(
        amount=transaction["amount"],
        category=category,
        info=transaction["info"],
        balance=transaction["balance"],
        date=date
    )
    return {
        "telegram_id": telegram_id,
        "text": text,
        "parse_mode": "markdown",
        "disable_notification": True
    }


async def push_user_notifications(user_id, transaction):
    """Push telegram notifications to SQS for user."""
    try:
        user = await User.get(user_id)
    except SWSDatabaseError:
        return

    if user.telegram_id is None:
        # skip notifications processing for user with deactivated telegram
        return

    notification_events = []
    if user.notifications_enabled:
        transaction_event = await get_transaction_event(user.telegram_id, transaction)
        notification_events.append(transaction_event)

    # TODO: get limit event

    async with aioboto3.resource("sqs") as sqs:
        queue = await sqs.get_queue_by_name(QueueName=config.SQS_NOTIFICATIONS_QUEUE_NAME)
        events = [queue.send_message(MessageBody=json.dumps(event)) for event in notification_events]
        await asyncio.gather(*events)

   # async with aioboto3.resource("sqs") as sqs:
   #     queue = await sqs.get_queue_by_name(QueueName=config.SQS_QUEUE_NAME)
