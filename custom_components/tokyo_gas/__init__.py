import logging

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

DOMAIN = "tokyo_gas"
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