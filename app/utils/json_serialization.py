from typing import Any

import orjson
from pydantic import BaseModel


def dumps(data: Any, default: Any = None, raw: bool = False) -> str | bytes:
    """
    Универсальная серриализация в json.

    - работает на pydantic моделях
    - быстрее стандартного json (потому что orjson на расте, да и по бенчам не плох)
    """
    if isinstance(data, BaseModel):
        data = data.dict()
    if not raw:
        return orjson.dumps(data, default=default, option=orjson.OPT_NON_STR_KEYS).decode("utf-8")

    return orjson.dumps(data, default=default, option=orjson.OPT_NON_STR_KEYS)


def loads(data: str | bytes) -> Any:
    """
    Десерриализация json jбъекта.

    - быстрее стандартного json
    - умеет парсить даты
    """
    return orjson.loads(data)
