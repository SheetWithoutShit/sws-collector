"""This module provides views for collector app."""

from http import HTTPStatus

from aiohttp import web
from aiojobs.aiohttp import spawn

from app.sio import TransactionEvent
from app.models.mcc import MCC
from app.models.transaction import Transaction
from app.utils.jwt import decode_token
from app.utils.errors import SWSTokenError, SWSDatabaseError
from app.utils.monobank import parse_transaction_response


monobank_routes = web.RouteTableDef()


@monobank_routes.view("/monobank/{user_collector_token}")
class MonobankWebhook(web.View):
    """Class that represent functionality to work with monobank webhook."""

    async def post(self):
        """Process transaction received from monobank webhook."""
        body = self.request.body
        config = self.request.app.config

        user_collector_token = self.request.match_info["user_collector_token"]
        try:
            payload = decode_token(user_collector_token, config.COLLECTOR_WEBHOOK_SECRET)
        except SWSTokenError:
            return web.json_response(
                data={
                    "success": False,
                    "message": "Forbidden. The provided token is not correct."
                },
                status=HTTPStatus.FORBIDDEN
            )

        user_id = payload["user_id"]
        transaction = parse_transaction_response(body)

        try:
            mcc_codes = [mcc.code for mcc in await MCC.get_all()]
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

        return web.json_response(
            data={
                "success": bool(inserted),
                "message": message,
                "user_id": user_id,
                "transaction": transaction
            },
            status=HTTPStatus.OK
        )
