from typing import Annotated

import fastapi
import pydantic

from schemas.core import Model
from schemas.shared import UserInfoOut


class UserFilterParams(Model):
    page: Annotated[int, fastapi.Query(description="Страница")] = 1
    rows_per_page: Annotated[int, fastapi.Query(description="Кол-во записей на странице")] = 25
    search: Annotated[str | None, fastapi.Query(description="Поиск пользователя")] = None
    sort_by: Annotated[str | None, fastapi.Query(description="Сортировка")] = "id"
    descending: Annotated[bool, fastapi.Query(description="Порядок сортировки")] = False


class UserList(UserFilterParams):
    data: list[UserInfoOut]
    count: int = pydantic.Field(0, description="Общее количество записей")
