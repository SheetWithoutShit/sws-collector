"""This module provides helper functionality with JWT."""

import jwt

from app.utils.errors import TokenError


def decode_token(token, secret_key):
    """Return decoded payload from json web token."""
    try:
        return jwt.decode(token, secret_key)
    except jwt.DecodeError:
        raise TokenError("The token is invalid.")
    except jwt.ExpiredSignatureError:
        raise TokenError("The token has expired.")
