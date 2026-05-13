import datetime
from typing import Annotated

import fastapi
import pydantic

from schemas.core import IdMixin, Model
from schemas.shared import UserInfoOut


class ChatMessageCreate(Model):
    message: str = pydantic.Field(..., min_length=1)


class ChatMessageBare(ChatMessageCreate, IdMixin):
    user_id: int
    user: UserInfoOut
    created_at: datetime.datetime


class MessageFilterParams(Model):
    page: Annotated[int, fastapi.Query()] = 1
    rows_per_page: Annotated[int, fastapi.Query()] = 1
    descending: Annotated[bool, fastapi.Query()] = False
    sort_by: Annotated[str, fastapi.Query()] = "created_at"


class MessageList(MessageFilterParams):
    data: list[ChatMessageBare]
