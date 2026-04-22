import os


class DBConfig:
    db_host = os.environ.get("DB_HOST")
    db_port = os.environ.get("DB_PORT")
    db_name = os.environ.get("DB_NAME")
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")

    db_async_pool_size = os.environ.get("DB_ASYNC_POOL_SIZE", 20)
    db_async_pool_max_overflow = os.environ.get("DB_ASYNC_POOL_MAX_OVERFLOW", 100)

    @property
    def async_db_conn_str(self) -> str:
        """Строка подключения к БД с использованием асинхронного драйвера"""
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?ssl=disable"


class AppSettings:
    """
    Настройки отвечающие за бизнес логику.
    """

    test_token = os.environ.get("TEST_TOKEN", None)  # TODO: убрать для прода/теста
    """Тестовый токен для проверки функциональности"""
    token_alive_hours = int(os.environ.get("TOKEN_ALIVE_HOURS", 4))
    """Время жизни токена в часах."""
    refresh_token_alive_hours = int(os.environ.get("REFRESH_TOKEN_ALIVE_HOURS", 24 * 7))
    """Время жизни refresh-токена в часах."""


class AppConfig:
    host: str = os.environ.get("HOST", "127.0.0.1")
    port: int = int(os.environ.get("PORT", 8000))

    secret = os.environ.get("SECRET")
    additional_debug: bool = (
        os.environ.get("ADDITIONAL_DEBUG", "false").lower() == "true"
    )


class Config(AppConfig, AppSettings, DBConfig):
    pass


config = Config()
