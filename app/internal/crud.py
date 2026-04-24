from http import HTTPStatus
from typing import TypeVar

import fastapi
from sqlalchemy import Select, select, func
from sqlalchemy.ext.asyncio import AsyncSession

_SearchType = TypeVar("_SearchType")


async def pagination_async(
    session: AsyncSession,
    model_class: type[_SearchType],
    page: int = 1,
    rows_per_page: int | None = 25,
    with_count: bool = True,
    query: Select = None,
) -> tuple[list[_SearchType], int]:
    """
    Выполняет запрос с пагинацией.
    """
    if query is None:
        query = select(model_class)

    if with_count:
        count_query = select(func.count("*")).select_from(query)
        rows_number = (await session.execute(count_query)).scalar_one()
    else:
        rows_number = None

    if rows_per_page:
        if rows_per_page < 0:
            raise fastapi.HTTPException(
                HTTPStatus.BAD_REQUEST, "Количество элементов на странице не может быть отрицательным"
            )
        query = query.limit(rows_per_page)

    if page < 1:
        raise fastapi.HTTPException(HTTPStatus.BAD_REQUEST, "Номер страницы должен быть больше или равен 1")
    final_query = query.offset(pagination_offset(page, rows_per_page))

    values = (await session.execute(final_query)).scalars().unique().all()
    return values, rows_number


def pagination_offset(page: int, rows_per_page: int | None = None) -> int:
    """
    Вычисление offset'а при запросе с пагинацией.
    """
    return (page - 1) * (rows_per_page or 0)
