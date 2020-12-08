"""This module provides functionality for user notifications."""

import asyncio
from datetime import datetime

from aiohttp import ClientSession

from app.models.user import User
from app.models.mcc import MCC
from app.models.transaction import Transaction
from app.utils.errors import DatabaseError
from app.utils.telegram import send_notification


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


async def get_transaction_notification(transaction):
    """Format a new transaction notification text."""
    try:
        category = await MCC.get_category(transaction["mcc"])
    except DatabaseError:
        category = "-"

    date = datetime.fromtimestamp(transaction["timestamp"]).strftime("%d.%m.%Y %H:%M:%S")
    notification = TRANSACTION_NOTIFICATION_TEXT.format(
        amount=transaction["amount"],
        category=category,
        info=transaction["info"],
        balance=transaction["balance"],
        date=date
    )

    return notification


async def get_limit_notification(user_id, mcc_code):
    """Format limit exceeding notification text."""
    try:
        limit = await User.get_limit(user_id, mcc_code)
    except DatabaseError:
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
    except DatabaseError:
        return

    if transactions_amount < limit["amount"]:
        return

    notification = LIMIT_NOTIFICATION_TEXT.format(
        category=limit["category_name"],
        limit=limit["amount"],
        amount=limit["amount"] - transactions_amount
    )

    return notification


async def send_user_notifications(user_id, transaction):
    """Send transaction, limit notifications to user."""
    try:
        user = await User.get(user_id)
    except DatabaseError:
        return

    if user.telegram_id is None or not user.notifications_enabled:
        # skip notifications processing for user with deactivated telegram
        # or disabled notifications
        return

    notification_events = []

    transaction_notification = await get_transaction_notification(transaction)
    notification_events.append(transaction_notification)

    limit_event = await get_limit_notification(user.id, transaction["mcc"])
    if limit_event:
        notification_events.append(limit_event)

    async with ClientSession() as aio_session:
        notifications = [
            send_notification(aio_session, user.telegram_id, notification)
            for notification in notification_events
        ]
        await asyncio.gather(*notifications)
