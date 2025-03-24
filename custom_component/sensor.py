"""Define the sensor for TokyoGas"""

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo, DeviceEntryType
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .util import get_statistic_id
from .const import STAT_ELECTRICITY_USAGE, DOMAIN


# pylint: disable=unused-argument
async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup the entry when forwarded from __init__.py"""

    async_add_entities(
        [
            TokyoGasSensor(
                entity_description=SensorEntityDescription(
                    key="electricity_usage_stat_id",
                    name="Electricity Usage Statistic ID",
                ),
                entry_id=entry.entry_id,
                value=get_statistic_id(entry.entry_id, STAT_ELECTRICITY_USAGE),
            )
        ]
    )


class TokyoGasSensor(SensorEntity):
    """Common Sensor class for TokyoGas"""

    def __init__(
            self,
            entry_id: str,
            entity_description: SensorEntityDescription,
            value: str = None,
    ):
        self.entity_description = entity_description
        self._attr_unique_id = f"{entry_id}_electricity_usage_statistic_id" # TODO a bit weird?
        self.entity_id = f"{DOMAIN}.{self._attr_unique_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id)},
            entry_type=DeviceEntryType.SERVICE,
        )

        if value:
            self._attr_native_value = value
