import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

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

    return True
