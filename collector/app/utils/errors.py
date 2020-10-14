"""This module provides custom errors."""


class BaseError(Exception):
    """Class that represents base error."""


class DatabaseError(BaseError):
    """Class that represents errors caused on interaction with database."""


class TokenError(BaseError):
    """Class that represents errors caused on interaction with auth token."""
