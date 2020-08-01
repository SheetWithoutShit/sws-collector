"""This module provides interactions with monobank data."""

COSTS_CONVERTER = 100.0


def parse_transaction_response(response):
    """Parse response from monobank API and return formatted transaction."""
    statement = response["data"]["statementItem"]
    return {
        "id": statement["id"],
        "amount": statement["amount"] / COSTS_CONVERTER,
        "balance": statement["balance"] / COSTS_CONVERTER,
        "cashback": statement["cashbackAmount"] / COSTS_CONVERTER,
        "info": statement["description"],
        "mcc": statement["mcc"],
        "timestamp": statement["time"]
    }
