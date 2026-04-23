import datetime
from typing import Callable

from sqlalchemy import DateTime, func
from sqlalchemy.orm import (
    declarative_base,
    declared_attr,
    Mapped,
    DeclarativeMeta,
    mapped_column,
)

Base: type[DeclarativeMeta] = declarative_base()


def fresh_timestamp() -> Callable[[], datetime.datetime]:
    """Небольшой хелпер для работы с timestamp на уровне ОРМа"""
    return func.timezone("UTC", func.now())


class TimestampMixin:
    @declared_attr
    def created_at(self) -> Mapped[datetime.datetime]:
        return mapped_column("created_at", DateTime, default=fresh_timestamp(), nullable=False)

    @declared_attr
    def updated_at(self) -> Mapped[datetime.datetime | None]:
        return mapped_column(
            "updated_at",
            DateTime,
            default=fresh_timestamp(),
            onupdate=fresh_timestamp(),
            nullable=False,
        )
