import pydantic

from schemas.core import IdMixin, Model
from schemas.shared import UserInfoOut


class ChatMessageCreate(Model):
    message: str = pydantic.Field(..., min_length=1)


class ChatMessageBare(ChatMessageCreate, IdMixin):
    user_id: int
    user: UserInfoOut
