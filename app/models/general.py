from sqlalchemy.orm import mapped_column, Mapped

from models.core import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = {"schema": "general"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(comment="Логин")
    password: Mapped[str] = mapped_column(comment="Пароль")
