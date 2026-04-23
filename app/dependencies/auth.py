import datetime

import fastapi
from fastapi import security

from schemas.auth import UserInfo
from utils.auth.jwt_generator import JWTGenerator


async def user_info_dep(
    token: security.HTTPAuthorizationCredentials = fastapi.Depends(security.HTTPBearer(bearerFormat="Bearer")),
) -> UserInfo:
    """
    Зависимость для получения информации о пользователе
    """
    if JWTGenerator.TEST_TOKEN and token.credentials == JWTGenerator.TEST_TOKEN:
        return UserInfo(
            id=1,
            updated_at=datetime.datetime.now(),
            login="admin",
        )

    return JWTGenerator.validate_jwt(token.credentials)
