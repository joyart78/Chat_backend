from typing import Any

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self


class Model(BaseModel):
    @classmethod
    async def model_validate_async(cls, obj: Any, session: AsyncSession) -> Self:
        mapper = lambda sess, obj: cls.model_validate(obj)
        return await session.run_sync(mapper, obj)

    class Config:
        from_attributes = True


class IdMixin(Model):
    id: int

    class Config(Model.Config):
        from_attributes = True


class ErrorSchema(Model):
    detail: str
