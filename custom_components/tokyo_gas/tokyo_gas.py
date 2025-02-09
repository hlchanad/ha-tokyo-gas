import logging
import random
from datetime import datetime, timedelta
from typing import TypedDict, List

import aiohttp

_LOGGER = logging.getLogger(__name__)


class Usage(TypedDict):
    date: datetime
    usage: float


class TokyoGas:
    def __init__(
            self,
            username: str,
            password: str,
            customer_number: str,
            domain: str,
    ):
        self._username = username
        self._password = password
        self._customer_number = customer_number
        self._domain = domain

    async def fetch_electricity_usage(
            self,
            session: aiohttp.ClientSession,
            date: datetime,
    ) -> List[Usage] | None:
        try:
            async with session.get(
                    url=f"{self._domain}/electricity-usages",
                    params={
                        "username": self._username,
                        "password": self._password,
                        "customerNumber": self._customer_number,
                        "date": date.strftime("%Y-%m-%d"),
                    },
                    timeout=60,  # scraper takes time
            ) as response:
                _LOGGER.debug("Got response from scraper, %s", await response.json())

                return [Usage(
                    date=datetime.fromisoformat(record["date"]),
                    usage=record["usage"],
                ) for record in await response.json()]
        except Exception as error:
            _LOGGER.error("Failed to get good response from scraper, %s", error)
            return None
