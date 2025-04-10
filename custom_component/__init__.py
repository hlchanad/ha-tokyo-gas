"""
Set up everything for TokyoGas custom component.
Forward platform settings.
Schedule daily tasks.
"""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_DOMAIN,
    CONF_TRIGGER_TIME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    CONF_CUSTOMER_NUMBER,
    STAT_ELECTRICITY_USAGE,
    CONF_STAT_LABEL_ELECTRICITY_USAGE,
    PLATFORMS,
)
from .fetch_electricity_usage import handle_service_fetch_electricity_usage, \
    create_schedule_handler_for_fetch_electricity_usage
from .statistics import insert_statistics, get_last_statistics
from .tokyo_gas import TokyoGas
from .util import get_statistic_id

_LOGGER = logging.getLogger(__name__)


# pylint: disable=unused-argument
def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up is called when Home Assistant is loading our component."""

    # Setup custom services
    hass.services.register(
        DOMAIN,
        "fetch_electricity_usage",
        handle_service_fetch_electricity_usage
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the entry (created via 'Devices/ Services')"""

    # Create API Client for this config_entry
    _tokyo_gas = TokyoGas(
        username=entry.data.get(CONF_USERNAME),
        password=entry.data.get(CONF_PASSWORD),
        customer_number=entry.data.get(CONF_CUSTOMER_NUMBER),
        domain=entry.data.get(CONF_DOMAIN),
    )

    # Store common API client to hass.data
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"tokyo_gas": _tokyo_gas}

    # Remove existing subscription if exist
    if DOMAIN in hass.data \
            and entry.entry_id in hass.data[DOMAIN] \
            and "unsubscribe" in hass.data[DOMAIN][entry.entry_id]:
        _LOGGER.debug("Somehow there is a existing schedule, unsubscribing to prevent memory leak")
        hass.data[DOMAIN][entry.entry_id]["unsubscribe"]()

    # Set up the scheduler
    hour, minute, second = entry.data.get(CONF_TRIGGER_TIME).split(":")
    hass.data[DOMAIN][entry.entry_id]["unsubscribe"] = async_track_time_change(
        hass,
        create_schedule_handler_for_fetch_electricity_usage(hass, entry, _tokyo_gas),
        hour=hour,
        minute=minute,
        second=second,
    )
    _LOGGER.info("Scheduled data fetching at %s:%s:%s everyday", hour, minute, second)

    # Delegate setup to each platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the entry (created via 'Devices/ Services')"""

    # Unsubscribe and remove data if exist
    if entry.entry_id in hass.data.get(DOMAIN, {}):
        entry_data = hass.data[DOMAIN][entry.entry_id]

        if "unsubscribe" in entry_data:
            entry_data["unsubscribe"]()

        del hass.data[DOMAIN][entry.entry_id]

        _LOGGER.info("Cleaned up data for integration (entry_id: %s)", entry.entry_id)

    # Delegate uploading to each platforms
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    return True
