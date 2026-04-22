import fastapi
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from utils.database import db_async_session

chat = APIRouter()


@chat.websocket("/message")
async def send_message(
    session: AsyncSession = fastapi.Depends(db_async_session)
):
    pass
