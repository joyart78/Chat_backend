import asyncio
from typing import TypeVar

from sqlalchemy import select, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket

from internal.crud import pagination_async
from models import ChatMessage
from schemas.chat import MessageList, ChatMessageBare

_UserId: int = TypeVar("_UserId")


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[_UserId, WebSocket] = {}

    async def add_socket_to_list(self, user_id: _UserId, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[user_id] = websocket

    async def remove_socket_from_list(self, user_id: _UserId) -> None:
        websocket = self.active_connections.pop(user_id)
        await websocket.close()

    async def send_to_user(self, user_id: _UserId, message: str) -> None:
        await self.active_connections[user_id].send_json(message)

    async def send_to_all(self, message: str) -> None:
        await asyncio.gather(*[connection.send_text(message) for connection in self.active_connections.values()])


ws_connection_manager = ConnectionManager()


async def get_messages(
    session: AsyncSession, page: int = 1, rows_per_page: int = 25, descending: bool = False, sort_by: str = "created_at"
) -> MessageList:
    desc_ = desc if descending else asc

    messages, count = await pagination_async(
        session,
        ChatMessage,
        page,
        rows_per_page,
        query=select(ChatMessage).order_by(desc_(getattr(ChatMessage, sort_by))),
    )
    data = [await ChatMessageBare.model_validate_async(mes, session) for mes in messages]

    return MessageList(page=page, rows_per_page=rows_per_page, descending=descending, sort_by=sort_by, data=data)
