import logging
import sys
import traceback
from http import HTTPStatus
from typing import Any, Callable
from urllib.request import Request

from fastapi import FastAPI
from starlette.responses import JSONResponse

from core.exceptions import NotAuthorizedError
from schemas.core import ErrorSchema
from utils.database import session_context


async def rollback_session(*args: Any, **kwargs: Any) -> None:
    try:
        session = session_context.get()
        await session.rollback()
    except LookupError:
        try:
            exc: Exception = kwargs.get("e") or args[1]
            print(  # noqa: T201
                "Unable to rollback a non existing session\n",
                *traceback.format_tb(exc.__traceback__),
                file=sys.stderr,
            )
        except IndexError:
            print(
                "Unable to found exception into exception handler;"
                ' Please pass exception as "e" argument.'
                "This also means, that it is not possible to catch a session for rollback "
                "and you should do it manually"
            )


def rollback_session_before(func: Callable) -> Callable:
    """
    Декоратор для сброса сессии перед началом обработки ошибки.

    **Предназначен для асинхронных функций**
    """

    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        await rollback_session(*args, **kwargs)
        return await func(*args, **kwargs)

    return wrapper


def add_exception_handlers(app: FastAPI) -> None:
    """
    Добавляет обработчики для ошибок к сервису.

    :param app: экземпляр сервиса
    :return:
    """
    logger = logging.getLogger("exception")

    @app.exception_handler(NotAuthorizedError)
    async def jwt_exception(request: Request, e: NotAuthorizedError) -> JSONResponse:
        """
        Обработчик для ошибок авторизации.
        """
        return JSONResponse(ErrorSchema(detail=str(e)).model_dump(), status_code=HTTPStatus.UNAUTHORIZED)
