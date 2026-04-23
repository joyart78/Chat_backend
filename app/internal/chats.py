import asyncio
from typing import TypeVar

from starlette.websockets import WebSocket

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

    async def send_user_error(self, user_id: _UserId, error: str) -> None:
        await self.active_connections[user_id].send_json(error)

    async def send_to_all(self, message: str) -> None:
        await asyncio.gather(*[connection.send_text(message) for connection in self.active_connections.values()])


ws_connection_manager = ConnectionManager()
