from datetime import datetime, timedelta
from typing import TypedDict, List


class Usage(TypedDict):
    date: datetime
    usage: float


class TokyoGas:
    def __init__(
            self,
            username: str,
            password: str,
            customer_number: str
    ):
        self._username = username
        self._password = password
        self._customer_number = customer_number

    def fetch_electricity_usage(self, date: datetime) -> List[Usage]:
        # TODO: dummy data temporarily
        hourly_data = [1, 2, 1.5, 2.5, 3, 1, 2, 1.8, 2.2, 1.7, 2.4, 1.6, 2.1, 1.9, 2.3, 1.4, 1.8, 2.7, 3.1, 1.2, 2.6,
                       1.3, 1.5, 2.8]

        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)

        return [
            Usage(
                date=start_date + timedelta(hours=i),
                usage=usage,
            ) for i, usage in enumerate(hourly_data)
        ]
