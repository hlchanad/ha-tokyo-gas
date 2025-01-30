import logging
from datetime import datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, UnitOfEnergy
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, CONF_CUSTOMER_NUMBER, STAT_ELECTRICITY_USAGE
from .statistics import insert_statistics
from .tokyo_gas import TokyoGas
from .util import get_statistic_id

_LOGGER = logging.getLogger(__name__)


def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up is called when Home Assistant is loading our component."""

    def handle_fetch_electricity_usage(call: ServiceCall):
        """Handle the service action call."""
        _LOGGER.info("Service called: %s.%s", call.domain, call.service)
        _LOGGER.info("Service data: %s", call.data)
        _LOGGER.info("Service context: %s", call.context.as_dict())

    hass.services.register(DOMAIN, "fetch_electricity_usage", handle_fetch_electricity_usage)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.info("async_setup_entry(), entry.entry_id: %s", entry.entry_id)
    _LOGGER.info("async_setup_entry(), entry.data: %s", entry.data)
    _LOGGER.info("async_setup_entry(), entry.unique_id: %s", entry.unique_id)
    _LOGGER.info("async_setup_entry(), entry.domain: %s", entry.domain)
    _LOGGER.info("async_setup_entry(), entry.source: %s", entry.source)
    _LOGGER.info("async_setup_entry(), entry.state: %s", entry.state)

    # entry.entry_id: 01JJAZ5GWMK3WCDRZQADJVMDRH
    # entry.data: {'username': 'test@example.com', 'password': 'aA123456'}
    # entry.unique_id: None
    # entry.domain: tokyo_gas
    # entry.source: user
    # entry.state: ConfigEntryState.SETUP_IN_PROGRESS

    _tokyo_gas = TokyoGas(
        username=entry.data.get(CONF_USERNAME),
        password=entry.data.get(CONF_PASSWORD),
        customer_number=entry.data.get(CONF_CUSTOMER_NUMBER, "dummy"),  # TODO
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = _tokyo_gas

    async def handle_fetch_statistics(now: datetime):
        _LOGGER.debug("handle_fetch_statistics(), now: %s", now)

        date = now.replace(hour=0, minute=0, second=0, microsecond=0)

        date.replace(month=1, day=28) # TODO: remove me

        insert_statistics(
            hass=hass,
            statistic_id=get_statistic_id(entry.entry_id, STAT_ELECTRICITY_USAGE),
            name="Electricity Usage",  # TODO configurable at ConfigFlow
            usages=_tokyo_gas.fetch_electricity_usage(date),
            unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        )

        _LOGGER.debug("added historical data for %s", date)

    async_track_time_change(
        hass,
        handle_fetch_statistics,
        hour=23,  # TODO: configurable at ConfigFlow
        minute=31,
        second=10,
    )

    _LOGGER.debug("async_setup_entry(), Scheduled handle_fetch_statistics()")

    return True
