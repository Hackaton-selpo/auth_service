from enum import Enum


class TokenType(str, Enum):
    """
    uses for cookie typing
    """

    access_token = "access_token"
    refresh_token = "refresh_token"
