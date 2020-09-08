"""This module provides views for collector app."""

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

        LOGGER.info("The monobank webhook for user=%s was successfully initialized.", user_id)
        return make_response(
            success=True,
            message=f"The monobank webhook was successfully applied for user={user_id}",
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

        mcc_code = transaction["mcc"] if transaction["mcc"] in mcc_codes else -1

        try:
            inserted = await Transaction.create_transaction(user_id, mcc_code, transaction)
        except SWSDatabaseError as err:
            inserted = False
            message = str(err)
        else:
            message = "A transaction was inserted successfully."
            await spawn(self.request, TransactionEvent.emit_new_transaction(user_id, transaction))

        response_data = {
            "user_id": user_id,
            "transaction": transaction
        }
        return make_response(
            success=bool(inserted),
            message=message,
            data=response_data,
            # We should return always 200 http status to monobank webhook
            http_status=HTTPStatus.OK
        )
