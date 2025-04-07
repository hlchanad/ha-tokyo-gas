"""Main logic flow for fetching and inserting electricity usages"""

import logging
from datetime import datetime, timedelta
from typing import TypedDict

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_registry import RegistryEntry
from homeassistant.helpers.issue_registry import IssueSeverity, async_create_issue

from .const import DOMAIN, STAT_ELECTRICITY_USAGE
from .statistics import insert_statistics
from .tokyo_gas import TokyoGas
from .util import get_statistic_id, get_statistic_name_for_electricity_usage

_LOGGER = logging.getLogger(__name__)


class StatisticMeta(TypedDict):
    """TypedDict for statistic meta data"""
    id: str
    name: str


async def _fetch_electricity_usages(
        hass: HomeAssistant,
        tokyo_gas: TokyoGas,
        statistic_meta: StatisticMeta,
        delta_days: int,
        report_issues: bool = False
):
    """Main logic for fetching and inserting historical electricity usages"""

    date = datetime.today() - timedelta(days=delta_days)

    usages = await tokyo_gas.fetch_electricity_usage(
        session=async_get_clientsession(hass),
        date=date,
    )

    if usages is None:
        # usages will be None if fail to fetch API
        if report_issues:
            # Raise a HA issue to draw attention
            async_create_issue(
                hass=hass,
                domain=DOMAIN,
                issue_id=statistic_meta["id"],
                is_fixable=False,
                is_persistent=True,
                severity=IssueSeverity.ERROR,
                translation_key="electricity_usage_error_api_fetch_failure",
            )
        else:
            _LOGGER.info("Skip inserting statistics because no data are scrapped")

        return

    is_any_non_null_usage = len(list(filter(lambda record: record["usage"], usages))) > 0
    if not is_any_non_null_usage:
        _LOGGER.info("Skip inserting statistics because all usage are null")
        return

    await insert_statistics(
        hass=hass,
        statistic_id=statistic_meta["id"],
        name=statistic_meta["name"],
        usages=usages,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    )

    _LOGGER.info("added historical data for %s", date.date())


async def handle_service_fetch_electricity_usage(call: ServiceCall):
    """Handle the service action call."""

    # Service Call args
    entity_id = call.data["statistic"]
    delta_days = call.data["delta_days"]

    # Get config_entry from hass
    entry: RegistryEntry | None = call.hass.data["entity_registry"].async_get(entity_id)
    if not entry or not entry.config_entry_id:
        raise TypeError(
            "Failed to find the entry data in TokyoGas integration. "
            "Please make sure the entity is from TokyoGas integration"
        )

    # Prepare variables for fetching electricity usages
    config_entry: ConfigEntry = call.hass.config_entries.async_get_entry(entry.config_entry_id)
    tokyo_gas = call.hass.data.get(DOMAIN)[entry.config_entry_id]["tokyo_gas"]
    statistic_id = call.hass.states.get(entity_id).state

    await _fetch_electricity_usages(
        hass=call.hass,
        tokyo_gas=tokyo_gas,
        statistic_meta=StatisticMeta(
            id=statistic_id,
            name=get_statistic_name_for_electricity_usage(config_entry)
        ),
        delta_days=delta_days,
        report_issues=False,
    )


def create_schedule_handler_for_fetch_electricity_usage(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        tokyo_gas: TokyoGas,
):
    """Create a handler for the hass scheduler"""

    # pylint: disable=unused-argument
    async def handle_scheduler_fetch_electricity_usage(now: datetime):
        """Handle the hass scheduler call"""

        await _fetch_electricity_usages(
            hass=hass,
            tokyo_gas=tokyo_gas,
            statistic_meta=StatisticMeta(
                id=get_statistic_id(config_entry.entry_id, STAT_ELECTRICITY_USAGE),
                name=get_statistic_name_for_electricity_usage(config_entry)
            ),
            delta_days=1,
            report_issues=True,
        )

    return handle_scheduler_fetch_electricity_usage
