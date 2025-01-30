import logging
from datetime import timezone
from typing import List

from homeassistant.components.recorder.models import StatisticMetaData, StatisticData
from homeassistant.components.recorder.statistics import async_add_external_statistics
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .tokyo_gas import Usage

_LOGGER = logging.getLogger(__name__)


def insert_statistics(
        hass: HomeAssistant,
        statistic_id: str,
        name: str,
        usages: List[Usage],
        unit_of_measurement: str,
):
    if not usages:
        _LOGGER.debug("No data in `usages`, skipping the process")
        return

    # TODO: fetch the last sum instead
    cumulative_sum = 0

    _LOGGER.debug("Going to insert external statistics")

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
