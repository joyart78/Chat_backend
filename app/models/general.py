from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from models.core import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = {"schema": "general"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(comment="Логин")
    password: Mapped[str] = mapped_column(comment="Пароль")


class ChatMessage(Base, TimestampMixin):
    __tablename__ = "chat_messages"
    __table_args__ = {"schema": "general"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message: Mapped[str] = mapped_column(comment="Сообщение")

    user_id = Column(Integer, ForeignKey("general.users.id"), nullable=False)

    user = relationship("User")
