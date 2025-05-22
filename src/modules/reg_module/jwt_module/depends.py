import datetime
import logging

import jwt
from fastapi import Depends, HTTPException, status, Request

from src.services.user_services import UserService
from .. import schemas
from ...shared import jwt_schemas
from src.core.config import load_config

config = load_config()


async def _validate_access_token_payload(
        payload: dict
) -> None:
    """
    payload.get unnecessary, because jwt.decode guarantee that payload will be filled
    function validating access token payload
    validate:
        date (token expiration date)
        token type (token type must be access)

    :param payload: dict with user information (all params in creator.py:create_access_token)
    :return: None
    :raise: fastapi HTTPException with code 401(unauthorized)
    """
    # validate token_type
    if payload[config.jwt.token_type_field] != jwt_schemas.TokenType.access_token.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token type"
        )
    # check expired date
    if datetime.datetime.now(datetime.UTC) > datetime.datetime.fromtimestamp(payload["exp"], datetime.UTC):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    # check free requests for un-auth user
    if payload["role"] == "guest":
        user_reqs = await UserService.get_user_reqs_count(user_id=payload["sub"])
        if user_reqs >= 20:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your free requests are over, you need to register a full account"
            )


def _get_refresh_token_from_cookies(
        request: Request,
) -> str:
    """
    function extract token from user cookies and validate it
    validate:
        token type (token type must be refresh)
    :param request: base fastapi request
    :return: refresh jwt token
    :raise: fastapi HTTPException with code 401(unauthorized) if token missed
    """
    cookie = request.cookies
    if not (token := cookie.get(jwt_schemas.TokenType.refresh_token.value)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not found, re-login please!"
        )
    return token


def get_user_id_from_refresh_token(
        refresh_token: str = Depends(_get_refresh_token_from_cookies),
) -> int:
    """
    extract user id from refresh jwt token
    to make new access token
    :param refresh_token: jwt token
    :return:int: user_id
    :raise: fastapi HTTPException with code 401(unauthorized) if token sign is wrong
    :raise: fastapi HTTPException with code 401(unauthorized) if token expired
    """
    try:
        payload: dict = jwt.decode(refresh_token, config.jwt.public_key_path,
                                   algorithms=[config.jwt.algorithm])
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    # check expired date
    if datetime.datetime.now(datetime.UTC) > datetime.datetime.fromtimestamp(payload["exp"], datetime.UTC):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    return int(payload['sub'])


def _get_access_token_from_cookie(
        request: Request
) -> str:
    """
    extract access token from user cookies
    :param request: base fastapi request
    :return: jwt access token
    :raise: fastapi HTTPException with code 401(unauthorized) if token is missed
    """
    cookie = request.cookies
    if not (token := cookie.get(jwt_schemas.TokenType.access_token.value)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not found"
        )
    return token


def _get_access_token_from_headers(
        request: Request,
) -> str:
    headers = request.headers
    if headers.get("Authorization"):
        return headers.get("Authorization").split(' ')[-1]
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token required"
    )


async def get_user_from_token(
        token: str = Depends(_get_access_token_from_headers),
) -> schemas.User:
    """
    extract access jwt token payload and return user schema
    :param token: access jwt token with payload
    :return: user schema with fields
    :raise: fastapi HTTPException with code 401(unauthorized) if token sign is wrong
    """
    try:
        payload: dict = jwt.decode(token, config.jwt.public_key_path, algorithms=[config.jwt.algorithm])
    except jwt.InvalidTokenError:
        logging.exception("invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    await _validate_access_token_payload(payload)
    return schemas.User(
        id=payload["sub"],
        email=payload["email"],
    )
