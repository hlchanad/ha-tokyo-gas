"""Common module for simple util"""
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME

from .const import DOMAIN, CONF_STAT_LABEL_ELECTRICITY_USAGE


def get_statistic_id(entry_id: str, identifier: str) -> str:
    """Format the statistic id"""

    # statistic_id has to be all lower case letters
    return f"{DOMAIN}:{entry_id.lower()}_{identifier}"


def get_statistic_name_for_electricity_usage(
        config_entry: ConfigEntry
):
    return config_entry.data.get(
        CONF_STAT_LABEL_ELECTRICITY_USAGE,
        f"Electricity Usage ({config_entry.data.get(CONF_USERNAME)})"
    )
