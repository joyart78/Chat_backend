import fastapi
from fastapi import APIRouter
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
    users_, count = await pagination_async(session, model_class=User, **filter_params.model_dump())

    data = [await UserInfoOut.model_validate_async(user, session) for user in users_]

    return UserList(data=data, count=count, **filter_params.model_dump())
