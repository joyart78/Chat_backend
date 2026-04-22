import calendar
import datetime
from typing import Any


def timestamp_to_unix(value: datetime.datetime | float | int | Any) -> float:
    """
    Проверка значение на возможность трансляции к временной метке.

    Необходимо для кейсов с JWT, когда нам нужно все временные метки перевести к UNIX времени в секундах

    :raises ValueError при несоответствии типов
    """
    if type(value) == datetime.datetime:
        value: datetime.datetime
        return calendar.timegm(value.utctimetuple())
    elif type(value) == float or type(value) == int:
        return value
    else:
        raise ValueError("Only timestamps allowed")
