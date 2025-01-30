import logging
from datetime import timezone
from typing import List

from homeassistant.components.recorder.models import StatisticMetaData, StatisticData
from homeassistant.components.recorder.statistics import async_add_external_statistics, get_last_statistics
from homeassistant.core import HomeAssistant
from homeassistant.helpers.recorder import get_instance

from .const import DOMAIN
from .tokyo_gas import Usage

_LOGGER = logging.getLogger(__name__)


async def insert_statistics(
        hass: HomeAssistant,
        statistic_id: str,
        name: str,
        usages: List[Usage],
        unit_of_measurement: str,
):
    if not usages:
        _LOGGER.debug("No data in `usages`, skipping the process")
        return

    last_stat = await get_instance(hass).async_add_executor_job(
        get_last_statistics,
        hass,
        1,
        statistic_id,
        False,
        {"sum"},
    )

    cumulative_sum = 0 if not last_stat else last_stat[statistic_id].pop()['sum']

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
            for usage in usages
        ],
    )

    _LOGGER.debug(f"Inserted data for {statistic_id}")
