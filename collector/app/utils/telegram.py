"""This module provides functionality for pushing notification event to SQS."""

import asyncio
import json
import logging
from datetime import datetime

import aioboto3

from app import config
from app.models.user import User
from app.models.mcc import MCC
from app.models.transaction import Transaction
from app.utils.errors import SWSDatabaseError


LOGGER = logging.getLogger(__name__)
LIMIT_NOTIFICATION_TEXT = \
    "*Limit Exceeded!* ⛔️\n\n" \
    "▪️ Category: *{category}*\n" \
    "▪️ Category Limit: *{limit}*\n" \
    "▪️ Exceeded by: *{amount}*\n"
TRANSACTION_NOTIFICATION_TEXT = \
    "*Transaction!* 💲\n\n" \
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


async def get_limit_event(user_id, telegram_id, mcc_code):
    """Push notification about limit exceeding to SQS for user."""
    try:
        limit = await User.get_limit(user_id, mcc_code)
    except SWSDatabaseError:
        return

    end_date = datetime.now()
    start_date = end_date.replace(day=1, hour=0, minute=0, second=0)
    try:
        transactions_amount = await Transaction.get_category_transactions_amount(
            user_id=user_id,
            category_id=limit.category_id,
            start_date=start_date,
            end_date=end_date
        )
    except SWSDatabaseError:
        return

    if transactions_amount > limit["amount"]:
        text = LIMIT_NOTIFICATION_TEXT.format(
            category=limit["category_name"],
            limit=limit["amount"],
            amount=limit["amount"] - transactions_amount
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

    limit_event = await get_limit_event(user.id, user.telegram_id, transaction["mcc"])
    if limit_event:
        notification_events.append(limit_event)

    async with aioboto3.resource("sqs") as sqs:
        queue = await sqs.get_queue_by_name(QueueName=config.SQS_NOTIFICATIONS_QUEUE_NAME)
        events = [queue.send_message(MessageBody=json.dumps(event)) for event in notification_events]
        await asyncio.gather(*events)
