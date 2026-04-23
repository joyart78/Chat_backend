from http import HTTPStatus

import fastapi
import jwt
import pydantic
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import NotAuthorizedError
from models.general import User
from schemas.auth import UserRegister, UserInfo, UserLogin, LoginOut
from utils.auth.jwt_generator import JWTGenerator
from utils.auth.token_schemas import RefreshTokenInfoOut
from utils.database import db_async_session
from utils.passwords import verify_password

auth = APIRouter()


@auth.post("/register")
async def register(
    session: AsyncSession = fastapi.Depends(db_async_session),
    data: UserRegister = fastapi.Body(...),
) -> UserInfo:
    """Регистрация"""

    user = await session.scalar(select(User).where(User.login == data.login))
    if user:
        raise fastapi.HTTPException(HTTPStatus.CONFLICT, detail="Пользователь с таким логином уже есть")

    user = User(**data.model_dump())

    session.add(user)
    await session.flush()

    return await UserInfo.model_validate_async(user, session)


@auth.post("/login")
async def login(
    session: AsyncSession = fastapi.Depends(db_async_session),
    data: UserLogin = fastapi.Body(...),
) -> LoginOut:
    """Логин"""
    unauthorized_error = fastapi.HTTPException(HTTPStatus.UNAUTHORIZED, detail="Логин или пароль не верные")

    user = await session.scalar(select(User).where(User.login == data.login))
    if not user:
        raise unauthorized_error

    if not verify_password(data.password, user.password):
        raise unauthorized_error

    user_info = UserInfo.model_validate(user)
    token = JWTGenerator.create_jwt(user_info)

    return LoginOut(token=token, user=user_info)


# noinspection PyProtectedMember
@auth.post("/refresh-token")
async def generate_refresh_token(
    session: AsyncSession = fastapi.Depends(db_async_session),
    token: str = fastapi.Form(...),
) -> LoginOut:
    """
    Получает новый jwt токен по refresh токену.
    """
    try:
        data = JWTGenerator._decode_jwt(token)
        info = RefreshTokenInfoOut(**data)
    except (pydantic.ValidationError, jwt.exceptions.DecodeError):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Неверный токен")
    except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.ExpiredSignatureError):
        msg = "Ваш токен более недействителен, пожалуйста авторизуйтесь снова"
        raise NotAuthorizedError(msg)

    user = await session.scalar(select(User).where(User.id == info.user_id))
    if not user:
        raise fastapi.HTTPException(HTTPStatus.NOT_FOUND, detail="Пользователь не найден")
    user_info = UserInfo.model_validate(user)

    user_last_update = user_info.updated_at.replace(tzinfo=None).timestamp()
    user_last_update_in_refresh = info.last_user_update.replace(tzinfo=None).timestamp()
    if int(user_last_update) != int(user_last_update_in_refresh):
        raise NotAuthorizedError("Ваш токен более недействителен, пожалуйста авторизуйтесь снова")

    token = JWTGenerator.create_jwt(user_info, refresh_token=token)

    return LoginOut(token=token, user=user_info)
