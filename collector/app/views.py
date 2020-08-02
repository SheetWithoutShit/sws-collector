"""This module provides views for collector app."""

from aiohttp import web
from core.jwt import decode_jwt

from app.utils.monobank import parse_transaction_response


routes = web.RouteTableDef()


@routes.view("/monobank/{token}")
class MonobankWebhook(web.View):
    """Class that represent functionality to work with monobank webhook."""

    def _check_permission(self):
        """Return user_id if provided token is correct."""
        token = self.request.match_info["token"]
        secret = self.request.app["constants"]["MONOBANK_WEBHOOK_SECRET"]
        decoded_token = decode_jwt(token, secret)
        if not decoded_token:
            return None

        user_id = decoded_token.get("user_id")
        return user_id

    async def post(self):
        """Receive transaction by monobank webhook and save transaction."""
        user_id = self._check_permission()
        if not user_id:
            return web.json_response(
                data={
                    "success": False,
                    "message": "Forbidden. The provided token was not correct."
                },
                status=403
            )

        data = await self.request.json()
        transaction_item = parse_transaction_response(data)

        transaction, mcc = self.request.app["transaction"], self.request.app["mcc"]

        mcc_code = transaction_item["mcc"]
        mcc_codes = await mcc.get_mcc_codes()
        mcc_code = mcc_code if mcc_code in mcc_codes else -1

        inserted = await transaction.insert_transaction(user_id, mcc_code, transaction_item)
        return web.json_response(
            data={
                "success": bool(inserted),
                "user_id": user_id,
                "transaction": transaction_item
            },
            status=200
        )
