import contextlib
from contextvars import ContextVar
from typing import AsyncGenerator, Callable, AsyncContextManager

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker, Session

from core.config import config
from utils import json_serialization

session_context: ContextVar[AsyncSession | Session] = ContextVar("session_context")

async_engine_default_params = {"poolclass": NullPool}


def async_session_factory(
    async_connection_string, **engine_params
) -> tuple[
    AsyncGenerator[AsyncSession, None],
    Callable[[], AsyncContextManager[AsyncSession]],
    AsyncEngine,
]:
    """
    Функция для создания асинхронной фабрики соединений с бд

    :param async_connection_string: connection url начинающийся с postgresql+asyncpg
    :param engine_params: параметры для AsyncEngine (настройки пула соединений)
    :return: генератор для использования в fastapi.Depends, контекстный менеджер
             бд для использования в любом ином месте, AsyncEngine для низкоуровнего взаимодействия
    """
    params = async_engine_default_params.copy()
    params.update(engine_params)

    engine = create_async_engine(async_connection_string, **params)
    # noinspection PyTypeChecker
    maker = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    async def get_async_session() -> AsyncSession:
        try:
            sess: AsyncSession = maker()
            session_context.set(sess)
            yield sess

        except Exception as e:
            await sess.rollback()
            raise e
        else:
            await sess.commit()
        finally:
            await sess.close()

    return get_async_session, contextlib.asynccontextmanager(get_async_session), engine


pool_params = {"poolclass": NullPool}
engine_params = {"json_serializer": json_serialization.dumps}

db_async_session, _db_async_session_manager, async_engine = async_session_factory(
    config.async_db_conn_str,
    **pool_params,
    **engine_params,
    echo=config.additional_debug,
)
