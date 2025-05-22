import hmac
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Response, status
from redis import Redis

from src.core.redis_initializer import get_redis
from . import schemas
from .depends import validate_code
from .jwt_module.creator import create_access_token, create_refresh_token
from .jwt_module.depends import get_user_from_token, get_user_id_from_refresh_token
from ..shared import jwt_schemas
from ..shared.jwt_schemas import TokenType
from ..smtp_celery_sender.send_code_to_user import send_verification_code
from ...core.config import load_config
from ...services.user_services import UserService

router: APIRouter = APIRouter(prefix="/auth", tags=["auth"])
config = load_config()


@router.post("/auth")
async def auth_user(
        email: Annotated[str, Form()]
) -> schemas.SuccessMessageSend:
    """
    first authorization router, user enter phone number and will receive 6-digits code
    :param email: validated phone number
    :return: success message
    :raise HTTPException with 500(some gone wrong)
    """
    try:
        send_verification_code.delay(email)
        return schemas.SuccessMessageSend(
            message="Verification code sent successfully",
        )
    except Exception as e:
        logging.exception("Exception")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e


@router.get("/verify_code")
async def verify_code(
        response: Response,
        user_auth_info: schemas.UserAuthInfo = Depends(validate_code),
        redis_client: Redis = Depends(get_redis),
):
    """
    second authorization handler, user has received the code, and will enter it to form with code
    set cookies with access and refresh token with httpOnly
    :param response: base fastapi response
    :param user_auth_info: validated user information
    :param redis_client: redis connection
    :return: None(only set cookies)
    :raise HTTPException 410 (when code not found in redis)
    :raise HTTPException 403 (when code is wrong)
    """
    # get code from redis using phone number
    backend_code_from_user = redis_client.get(user_auth_info.email)
    if backend_code_from_user is None:
        raise HTTPException(
            status_code=status.HTTP_410_GONE, detail="Code lifetime is expired"
        )
    # using to avoid time attack
    if hmac.compare_digest(backend_code_from_user, str(user_auth_info.code)):
        # delete code from redis
        redis_client.delete(user_auth_info.email)
        # insert or get user from db
        user_model = await UserService.create_user(user_auth_info.email, role_id=1)

        # user auth success!
        # create jwt tokens
        access_token: str = create_access_token(user=user_model, role="user")
        refresh_token: str = create_refresh_token(user_model.id)

        # set jwt tokens in cookies
        response.set_cookie(
            key=jwt_schemas.TokenType.refresh_token.value,
            value=refresh_token,
            httponly=True,
            secure=False,  # MAKE TRUE ON PRODUCTION
        )
        return {TokenType.access_token: access_token}

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Wrong code")


@router.get("/verify_guest")
async def verify_guest() -> schemas.AccessTokenSchema:
    user = await UserService.create_user(email=None, role_id=2)
    token = create_access_token(user=user, role="guest")

    return {"access_token": token}


@router.get("/refresh_token")
async def get_new_access_token(
        response: Response,
        user_id: int = Depends(get_user_id_from_refresh_token),
):
    """
    using to update access token
    :param response:
    :param user_id: user id from refresh token(token after validation)
    :return: None (set new access token in cookies)
    """
    # get user from database
    user_model = await UserService.get_user_by_id(user_id)
    # set jwt
    access_token = create_access_token(user=user_model, role="user")
    return {
        TokenType.access_token: access_token,
    }


@router.get("/logout")
async def logout(response: Response, _=Depends(get_user_from_token)):
    """
    delete user cookies
    :param response:
    :param _: uses to check that user logged
    :return: None (delete both tokens cookies)
    """

    response.delete_cookie(
        key=jwt_schemas.TokenType.refresh_token.value,
    )


@router.get("/protected")
async def start_page(_=Depends(get_user_from_token)):
    """
    random protected hand
    :param _: uses to check that user logged
    :return:
    """
    return {"status": "success"}
