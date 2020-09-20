"""This module provides views for collector app."""

import asyncio
import logging
from http import HTTPStatus

from aiohttp import web
from aiojobs.aiohttp import spawn

from app.sio import TransactionEvent
from app.models.mcc import MCC
from app.models.transaction import Transaction
from app.utils.jwt import decode_token
from app.utils.response import make_response
from app.utils.errors import SWSTokenError, SWSDatabaseError
from app.utils.monobank import parse_transaction_response
from app.utils.telegram import push_user_notifications


monobank_routes = web.RouteTableDef()
LOGGER = logging.getLogger(__name__)


@monobank_routes.view("/monobank/{user_collector_token}")
class MonobankWebhook(web.View):
    """Class that represent functionality to work with monobank webhook."""

    def parse_user_token(self):
        """Return user id from token in request path."""
        user_collector_token = self.request.match_info["user_collector_token"]
        payload = decode_token(user_collector_token, self.request.app.config.COLLECTOR_WEBHOOK_SECRET)
        return payload["user_id"]

    async def get(self):
        """Process first get request by monobank webhook."""
        try:
            user_id = self.parse_user_token()
        except (SWSTokenError, KeyError):
            return web.json_response(
                data={
                    "success": False,
                    "message": "Forbidden. The provided token is not correct."
                },
                status=HTTPStatus.FORBIDDEN
            )

        LOGGER.info("The monobank webhook for user=%s was initialized.", user_id)
        return make_response(
            success=True,
            message=f"Success. The monobank webhook was applied for user={user_id}",
            http_status=HTTPStatus.OK
        )

    async def post(self):
        """Process transaction received from monobank webhook."""
        body = self.request.body

        try:
            user_id = self.parse_user_token()
        except (SWSTokenError, KeyError):
            return web.json_response(
                data={
                    "success": False,
                    "message": "Forbidden. The provided token is not correct."
                },
                status=HTTPStatus.FORBIDDEN
            )

        transaction = parse_transaction_response(body)

        try:
            mcc_codes = await MCC.get_codes()
        except SWSDatabaseError:
            mcc_codes = []

        mcc_code = transaction["mcc"]
        if mcc_code not in mcc_codes:
            LOGGER.error("Could not find MCC code=%s in database.", mcc_code)
            mcc_code = -1

        try:
            await Transaction.create_transaction(user_id, mcc_code, transaction)
        except SWSDatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                # We should return always 200 http status to monobank webhook
                http_status=HTTPStatus.OK
            )
        else:
            await asyncio.gather(
                spawn(self.request, TransactionEvent.emit_new_transaction(user_id, transaction)),
                spawn(self.request, push_user_notifications(user_id, transaction))
            )

        response_data = {
            "user_id": user_id,
            "transaction": transaction
        }
        return make_response(
            success=True,
            message="Success. The transaction was inserted.",
            data=response_data,
            http_status=HTTPStatus.OK
        )
