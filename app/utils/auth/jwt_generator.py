import datetime
import logging

import jwt
import pydantic
from core.config import config
from core.exceptions import NotAuthorizedError
from schemas.auth import UserInfo, UserInfoJWT
from utils.auth.token_schemas import (
    RefreshTokenInfoIn,
    Token,
    TokenInfo,
    UserInfoJWTUnix,
)


class JWTGenerator:
    """
    Синглтон для работы с jwt.
    """

    JWT_SECRET = config.secret
    DEFAULT_ALGORITHM = "HS256"  # не менять просто так, на него завязана centrifugo
    TOKEN_ALIVE_HOURS = datetime.timedelta(hours=config.token_alive_hours)
    REFRESH_TOKEN_ALIVE_HOURS = datetime.timedelta(hours=config.refresh_token_alive_hours)

    logger = logging.getLogger("JWTGenerator")

    TEST_TOKEN = config.test_token

    @classmethod
    def _encode_jwt(cls, data: dict) -> str:
        return jwt.encode(data, key=cls.JWT_SECRET, algorithm=cls.DEFAULT_ALGORITHM)

    @classmethod
    def _decode_jwt(cls, token: str) -> dict:
        return jwt.decode(token, cls.JWT_SECRET, algorithms=[cls.DEFAULT_ALGORITHM])

    @classmethod
    def create_jwt(cls, user: UserInfo, refresh_token: str | None = None) -> Token:
        """
        Создаёт jwt токен из данных пользователя.

        :param user:
        :return:
        """
        user = UserInfoJWTUnix(**user.model_dump())
        created_at = datetime.datetime.utcnow()
        expired_at = created_at + cls.TOKEN_ALIVE_HOURS
        refresh_expired_at = created_at + cls.REFRESH_TOKEN_ALIVE_HOURS

        if not refresh_token:
            refresh_info = RefreshTokenInfoIn(
                user_id=user.id,
                upd=user.updated_at,
                exp=refresh_expired_at,
            ).model_dump(by_alias=True)
            refresh_token = cls._encode_jwt(refresh_info)

        token_info = TokenInfo(user=user, refresh_token=refresh_token, exp=expired_at, iat=created_at)

        token = cls._encode_jwt(token_info.model_dump(by_alias=True))

        return token

    @classmethod
    def parse_jwt(cls, token: Token) -> TokenInfo | None:
        """
        Получает информацию из jwt токена.
        """
        decoded_jwt = None
        try:
            decoded_jwt = cls._decode_jwt(token)
            user_info = TokenInfo(**decoded_jwt)
        except (jwt.InvalidTokenError, jwt.exceptions.InvalidSignatureError) as e:  # noqa: F841
            cls.logger.exception(
                f'Failed to decode token: "...{token[-10:]}"',
                extra={"for_debug": token},
            )
        except pydantic.ValidationError as e:  # noqa: F841
            cls.logger.exception(f'Got some unparsed dict from token "{decoded_jwt}"')
        else:
            return user_info

        return None

    @classmethod
    def validate_jwt(cls, token: Token) -> UserInfoJWT:
        """
        Проверяет jwt токен на валидность и возвращает информацию о пользователе.

        :raises NotAuthorized
        """
        user_info = cls.parse_jwt(token)

        if not user_info:
            err_msg = "Неверный токен авторизации"
            raise NotAuthorizedError(err_msg)

        expired_at = datetime.datetime.fromtimestamp(
            user_info.token_expired_at,
            tz=datetime.timezone.utc,
        ).replace(tzinfo=None)
        current_time = datetime.datetime.utcnow()
        if expired_at < current_time:
            err_msg = "Ваш токен более недействителен, пожалуйста авторизуйтесь снова"
            raise NotAuthorizedError(err_msg)

        return UserInfoJWT(**user_info.user.dict())

    @classmethod
    def mask_jwt(cls, token: Token) -> str:
        """Обрезает токен оставляя только первые 2 его части."""
        return ".".join(token.split(".")[:2])
