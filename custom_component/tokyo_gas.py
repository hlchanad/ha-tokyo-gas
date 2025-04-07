"""Wrap API calls to the custom addon, which scrapes data from TokyoGas"""

import logging
from datetime import datetime
from typing import TypedDict, List

import aiohttp

_LOGGER = logging.getLogger(__name__)


class Usage(TypedDict):
    """TypedDict for the daily usage"""
    date: datetime
    usage: float


class TokyoGas:
    """Wrapper for API calls to the custom addon"""

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

    async def verify_credentials(
            self,
            session: aiohttp.ClientSession,
    ) -> bool:
        """Call the POST /login API to see if the credentials are good"""

        async with session.post(
                url=f"{self._domain}/login",
                json={
                    "username": self._username,
                    "password": self._password,
                    "customerNumber": self._customer_number,
                },
        ) as response:
            _LOGGER.info("Login result, status: %s", response.status)
            return 200 <= response.status < 300


    async def fetch_electricity_usage(
            self,
            session: aiohttp.ClientSession,
            date: datetime,
    ) -> List[Usage] | None:
        """Call the GET /electricity-usages API to fetch daily electricity usage"""

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
