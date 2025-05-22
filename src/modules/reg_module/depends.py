from fastapi import HTTPException

from . import schemas


def validate_code(
        code: int,
        email: str
) -> schemas.UserAuthInfo:
    """
    validate full user information
    :param code: 6-digit code
    :param email: string
    :return: validated code and phone_number in UserAuthInfo schema
    :raise: HTTPException with 422(validation error)
    """
    try:
        return schemas.UserAuthInfo(
            email=email,
            code=code,
        )
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid format of code or phone number",
        )
