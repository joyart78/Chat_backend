import fastapi
from fastapi import APIRouter
from sqlalchemy import select, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.auth import user_info_dep
from internal.crud import pagination_async
from models import User
from schemas.auth import UserInfo
from schemas.shared import UserInfoOut
from schemas.users import UserFilterParams, UserList
from utils.database import db_async_session

users = APIRouter()


@users.get("")
async def get_users(
    session: AsyncSession = fastapi.Depends(db_async_session),
    filter_params: UserFilterParams = fastapi.Depends(UserFilterParams),
    author: UserInfo = fastapi.Depends(user_info_dep),
) -> UserList:
    """Получить список пользователей"""
    query = select(User)
    if filter_params.search:
        query = query.where(User.login.ilike(f"%{filter_params.search}%"))
    if filter_params.sort_by:
        order_direction = desc if filter_params.descending else asc
        query = query.order_by(order_direction(getattr(User, filter_params.sort_by)))

    users_, count = await pagination_async(session, model_class=User, query=query, **filter_params.model_dump())

    data = [await UserInfoOut.model_validate_async(user, session) for user in users_]

    return UserList(data=data, count=count, **filter_params.model_dump())
