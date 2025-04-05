import logging
from datetime import datetime, timedelta

from homeassistant.const import UnitOfEnergy, CONF_USERNAME
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.issue_registry import IssueSeverity, async_create_issue

from .const import DOMAIN, CONF_STAT_LABEL_ELECTRICITY_USAGE
from .statistics import get_last_statistics, insert_statistics
from .tokyo_gas import TokyoGas

_LOGGER = logging.getLogger(__name__)


async def _fetch_electricity_usages(
        hass: HomeAssistant,
        tokyo_gas: TokyoGas,
        statistic_id: str,
        statistic_name: str,
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
        if report_issues:
            # Raise a HA issue to draw attention
            async_create_issue(
                hass=hass,
                domain=DOMAIN,
                issue_id=statistic_id,
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
        statistic_id=statistic_id,
        name=statistic_name,
        usages=usages,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    )

    _LOGGER.info("added historical data for %s", date)


async def handle_fetch_electricity_usage(call: ServiceCall):
    """Handle the service action call."""

    # Service Call args
    entity_id = call.data["statistic"]
    delta_days = call.data["delta_days"]

    # Get config_entry/ data from hass
    entry = call.hass.data["entity_registry"].async_get(entity_id)
    if not entry or not entry.config_entry_id:
        _LOGGER.error("Failed to find the entry data in TokyoGas integration")
        raise Exception("Failed to find the entry data in TokyoGas integration")

    # Prepare variables for fetching electricity usages
    config_entry = call.hass.config_entries.async_get_entry(entry.config_entry_id)
    _tokyo_gas = call.hass.data.get(DOMAIN)[entry.config_entry_id]["tokyo_gas"]
    statistic_id = call.hass.states.get(entity_id).state

    await _fetch_electricity_usages(
        hass=call.hass,
        tokyo_gas=_tokyo_gas,
        statistic_id=statistic_id,
        statistic_name=config_entry.data.get(
            CONF_STAT_LABEL_ELECTRICITY_USAGE,
            f"Electricity Usage ({config_entry.data.get(CONF_USERNAME)})"
        ),
        delta_days=delta_days,
        report_issues=False,
    )
