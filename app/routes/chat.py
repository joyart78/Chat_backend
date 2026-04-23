import logging
from http import HTTPStatus

import fastapi
from fastapi import APIRouter, WebSocket
from pydantic import ValidationError
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.websockets import WebSocketDisconnect

from core.exceptions import NotAuthorizedError
from internal.chats import ws_connection_manager
from models import ChatMessage, User
from schemas.chat import ChatMessageCreate, ChatMessageBare
from utils.auth.jwt_generator import JWTGenerator
from utils.database import db_async_session

chat = APIRouter()


@chat.websocket("/ws")
async def get_messages(
    websocket: WebSocket,
    session: AsyncSession = fastapi.Depends(db_async_session),
) -> None:
    user_token = websocket.headers.get("authorization", "").replace("Bearer ", "")
    authorized_error = websocket.close(status.WS_1008_POLICY_VIOLATION, reason="Ваш токен не действителен")

    try:
        user = JWTGenerator.validate_jwt(user_token)
    except NotAuthorizedError:
        await authorized_error

    user_exist = await session.scalar(select(exists(User).where(User.id == user.id)))
    if not user_exist:
        await authorized_error

    await ws_connection_manager.add_socket_to_list(user.id, websocket)

    is_active = True
    while is_active:
        try:
            data: str = await websocket.receive_text()
            data: ChatMessageCreate = ChatMessageCreate.model_validate_json(data)

            message = ChatMessage(message=data.message, user_id=user.id)
            session.add(message)
            await session.commit()

            message = await ChatMessageBare.model_validate_async(message, session)
            await ws_connection_manager.send_to_all(str(message))

        except ValidationError as validation_error:
            await ws_connection_manager.send_user_error(user.id, str(validation_error))
        except WebSocketDisconnect:
            await ws_connection_manager.remove_socket_from_list(user.id)
            is_active = False
        except Exception as error:
            logging.getLogger("ws_chat").error(error)
