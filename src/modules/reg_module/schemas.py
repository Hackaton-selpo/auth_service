from pydantic import BaseModel, field_validator, EmailStr
import re


class SuccessMessageSend(BaseModel):
    message: str


class User(BaseModel):
    id: int
    email: EmailStr


class UserAuthInfo(BaseModel):
    code: int
    email: EmailStr
