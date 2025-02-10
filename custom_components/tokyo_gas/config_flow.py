from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlowResult, ConfigFlow
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_DOMAIN, CONF_TRIGGER_TIME
from homeassistant.helpers.selector import TextSelector, TextSelectorType, TextSelectorConfig, TimeSelector, \
    TimeSelectorConfig

from . import DOMAIN, CONF_CUSTOMER_NUMBER

_LOGGER = logging.getLogger(__name__)


class TokyoGasConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
            self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            # Store the user input and create a config entry
            return self.async_create_entry(
                title=user_input.get("username"),  # Name displayed in the UI
                data=user_input,  # Store the user input for future use
            )

        # Display the form
        return self.async_show_form(
            step_id="user",
            description_placeholders=None,
            data_schema=vol.Schema({
                vol.Required(CONF_USERNAME): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.EMAIL, autocomplete="username")
                ),
                vol.Required(CONF_PASSWORD): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.PASSWORD, autocomplete="current-password")
                ),
                vol.Required(CONF_CUSTOMER_NUMBER): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT)
                ),
                vol.Required(CONF_DOMAIN, default="http://tokyo_gas_scraper:3000"): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.URL)
                ),
                vol.Required(CONF_TRIGGER_TIME, default="14:00:00"): TimeSelector(TimeSelectorConfig())
            }),
        )
