from pydantic import BaseModel, EmailStr


class SuccessMessageSend(BaseModel):
    message: str


class User(BaseModel):
    id: int
    email: EmailStr


class UserAuthInfo(BaseModel):
    code: int
    email: EmailStr


class AccessTokenSchema(BaseModel):
    access_token: str


class UserRequestsResponse(BaseModel):
    reqs: int
