"""Util methods for wrapping HA statistics related logic"""

import logging
from datetime import timezone, datetime
from typing import List, Optional

from homeassistant.components.recorder.models import StatisticMetaData, StatisticData
from homeassistant.components.recorder.statistics import async_add_external_statistics
from homeassistant.core import HomeAssistant
from homeassistant.helpers.recorder import get_instance
from sqlalchemy import text

from .const import DOMAIN
from .tokyo_gas import Usage

_LOGGER = logging.getLogger(__name__)


def _get_last_statistics(
        hass: HomeAssistant,
        statistic_id: str,
        date: Optional[datetime] = None,
):
    """Query database to get the last statistic record, w.r.t. `date`"""

    with get_instance(hass).engine.connect() as connection:
        # Get the last record OR the record right before given timestamp
        query = text("""
               SELECT 
                   s.start_ts, 
                   s.state, 
                   s.sum
               FROM statistics s
               LEFT JOIN statistics_meta sm ON s.metadata_id = sm.id
               WHERE
                   sm.statistic_id = :statistic_id
                   AND (:timestamp IS NULL OR s.start_ts < :timestamp)
               ORDER BY s.start_ts DESC
               LIMIT 1
           """)

        result = connection.execute(query, {
            "statistic_id": statistic_id,
            "timestamp": datetime.timestamp(date) if date else None,
        }).fetchone()

        _LOGGER.debug("DB query result: %s", result)

        return {
            "start_ts": result[0],
            "state": result[1],
            "sum": result[2]
        } if result else None


async def get_last_statistics(
        hass: HomeAssistant,
        statistic_id: str,
        date: Optional[datetime] = None,
):
    """Return the last statistics of a specific statistic_id"""

    result = await get_instance(hass).async_add_executor_job(
        _get_last_statistics,
        hass,
        statistic_id,
        date,
    )

    return result


async def insert_statistics(
        hass: HomeAssistant,
        statistic_id: str,
        name: str,
        usages: List[Usage],
        unit_of_measurement: str,
):
    """Insert a list of records to a specific statistic_id"""

    if not usages:
        _LOGGER.debug("No data in `usages`, skipping the process")
        return

    last_stat = await get_last_statistics(hass, statistic_id, usages[0]["date"])

    cumulative_sum = 0 if not last_stat else last_stat["sum"]

    _LOGGER.debug(
        "first datetime: %s, last_stat: %s, cumulative_sum: %s",
        usages[0]["date"],
        last_stat,
        cumulative_sum
    )

    # Insert the new statistics records
    async_add_external_statistics(
        hass,
        metadata=StatisticMetaData(
            source=DOMAIN,
            statistic_id=statistic_id,
            name=name,
            unit_of_measurement=unit_of_measurement,
            has_mean=False,
            has_sum=True,
        ),
        statistics=[
            StatisticData(
                start=usage["date"].astimezone(timezone.utc),
                state=usage["usage"],
                sum=(cumulative_sum := cumulative_sum + usage["usage"]),
            )
            for usage in usages if usage["usage"]
        ],
    )

    _LOGGER.debug("Inserted data for %s", statistic_id)
