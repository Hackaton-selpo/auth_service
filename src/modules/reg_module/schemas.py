from typing import Optional

from pydantic import BaseModel, EmailStr


class EmailForm(BaseModel):
    email: EmailStr


class SuccessMessageSend(BaseModel):
    message: str


class User(BaseModel):
    id: int
    email: Optional[EmailStr] = None
    role: str


class UserAuthInfo(BaseModel):
    code: str
    email: EmailStr


class AccessTokenSchema(BaseModel):
    access_token: str


class UserRequestsResponse(BaseModel):
    reqs: int
