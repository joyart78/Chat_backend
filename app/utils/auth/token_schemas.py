# ruff: noqa: N805, D102, D101
import datetime
from typing import Literal

import pydantic
from schemas.auth import UserInfoJWT
from utils.utils import timestamp_to_unix

Token = str


class RefreshTokenInfoIn(pydantic.BaseModel):
    """
    Информация, содержащаяся в JWT refresh токене.

    Используется для добавления информации в токен.
    """

    user_id: int
    exp: float | datetime.datetime = pydantic.Field(..., description="expired_at")
    upd: float | datetime.datetime = pydantic.Field(..., description="last_user_update")
    typ: Literal["refresh"] = pydantic.Field("refresh")

    @pydantic.field_validator("exp", "upd", mode="before")
    def validate_timestamps(cls, value: datetime.datetime) -> float:
        return timestamp_to_unix(value)


class UserInfoJWTUnix(UserInfoJWT):
    updated_at: float | datetime.datetime = pydantic.Field(...)

    @pydantic.field_validator("updated_at", mode="before")
    def validate_updated_at(cls, value: datetime.datetime) -> float:
        return timestamp_to_unix(value)


class RefreshTokenInfoOut(pydantic.BaseModel):
    """
    Информация, содержащаяся в JWT refresh токене.

    Используется для получения информации из токена.
    """

    user_id: int
    expired_at: datetime.datetime = pydantic.Field(..., alias="exp")
    last_user_update: datetime.datetime = pydantic.Field(..., alias="upd")
    type: Literal["refresh"] = pydantic.Field(alias="typ")


class TokenInfo(pydantic.BaseModel):
    """
    Дополнительная информация содержащаяся в JWT токене
    """

    sub: str | None = pydantic.Field(None, description="Он же id")
    user: UserInfoJWT
    token_expired_at: float | datetime.datetime = pydantic.Field(..., alias="exp")
    token_created_at: float | datetime.datetime = pydantic.Field(..., alias="iat")
    refresh_token: str

    @pydantic.model_validator(mode="after")
    def set_sub(self) -> "TokenInfo":
        self.sub = str(self.user.id)
        return self

    @pydantic.field_validator("token_expired_at", mode="before")
    def validate_token_expired_at(cls, value: datetime.datetime) -> float:
        return timestamp_to_unix(value)

    @pydantic.field_validator("token_created_at", mode="before")
    def validate_token_created_at(cls, value: datetime.datetime) -> float:
        return timestamp_to_unix(value)
