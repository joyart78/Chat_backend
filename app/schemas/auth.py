import datetime

import pydantic

from schemas.core import Model, IdMixin
from utils.passwords import generate_password_hash


class UserRegister(Model):
    login: str
    password: str

    @pydantic.field_validator("password")
    def hash_password(cls, val: str) -> str:
        return generate_password_hash(val)


class UserLogin(Model):
    login: str
    password: str


class UserInfo(Model):
    id: int
    login: str

    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class UserInfoJWT(Model):
    """
    Данные, хранящиеся в JWT токене
    """

    id: int = pydantic.Field(...)
    login: str


class LoginOut(Model):
    token: str = pydantic.Field(..., description="JWT токен пользователя")
    user: UserInfo
