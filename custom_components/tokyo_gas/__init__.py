import logging
from datetime import datetime, timezone, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, UnitOfEnergy, CONF_DOMAIN, CONF_TRIGGER_TIME
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, CONF_CUSTOMER_NUMBER, STAT_ELECTRICITY_USAGE, CONF_STAT_LABEL_ELECTRICITY_USAGE
from .statistics import insert_statistics, get_last_statistics
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
    _LOGGER.debug("async_setup_entry(), entry.entry_id: %s", entry.entry_id)
    _LOGGER.debug("async_setup_entry(), entry.data: %s", entry.data)
    _LOGGER.debug("async_setup_entry(), entry.unique_id: %s", entry.unique_id)
    _LOGGER.debug("async_setup_entry(), entry.domain: %s", entry.domain)
    _LOGGER.debug("async_setup_entry(), entry.source: %s", entry.source)
    _LOGGER.debug("async_setup_entry(), entry.state: %s", entry.state)

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
        domain=entry.data.get(CONF_DOMAIN),
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"tokyo_gas": _tokyo_gas}

    async def handle_fetch_statistics(now: datetime):
        _LOGGER.debug("handle_fetch_statistics(), now: %s", now)

        date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        date = date - timedelta(days=1)  # get data of yesterday

        usages = await _tokyo_gas.fetch_electricity_usage(session=async_get_clientsession(hass), date=date)

        if usages is None:
            _LOGGER.info("Skip inserting statistics because no data are scrapped")
            return

        is_any_non_null_usage = len(list(filter(lambda record: record["usage"], usages))) > 0
        if not is_any_non_null_usage:
            _LOGGER.info("Skip inserting statistics because all usage are null")
            return

        statistic_id = get_statistic_id(entry.entry_id, STAT_ELECTRICITY_USAGE)

        last_stat = await get_last_statistics(hass, statistic_id)
        if last_stat:
            last_stat_date = datetime.fromtimestamp(last_stat[statistic_id].pop()["start"], timezone.utc)
            first_new_stat_date = usages[0].get("date")

            if first_new_stat_date <= last_stat_date:
                _LOGGER.info("Skip inserting statistics because data exist on %s", date)
                return

        await insert_statistics(
            hass=hass,
            statistic_id=statistic_id,
            name=entry.data.get(
                CONF_STAT_LABEL_ELECTRICITY_USAGE,
                f"Electricity Usage ({entry.data.get(CONF_USERNAME)})"
            ),
            usages=usages,
            unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        )

        _LOGGER.info("added historical data for %s", date)

    if DOMAIN in hass.data \
            and entry.entry_id in hass.data[DOMAIN] \
            and "unsubscribe" in hass.data[DOMAIN][entry.entry_id]:
        _LOGGER.debug("Somehow there is a existing schedule, unsubscribing to prevent memory leak")
        hass.data[DOMAIN][entry.entry_id]["unsubscribe"]()

    hour, minute, second = entry.data.get(CONF_TRIGGER_TIME).split(":")

    hass.data[DOMAIN][entry.entry_id]["unsubscribe"] = async_track_time_change(
        hass,
        handle_fetch_statistics,
        hour=hour,
        minute=minute,
        second=second,
    )

    _LOGGER.info("Scheduled data fetching at %s:%s:%s everyday", hour, minute, second)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if entry.entry_id in hass.data.get(DOMAIN, {}):
        entry_data = hass.data[DOMAIN][entry.entry_id]

        if "unsubscribe" in entry_data:
            entry_data["unsubscribe"]()

        del hass.data[DOMAIN][entry.entry_id]

        _LOGGER.info("Cleaned up data for integration (entry_id: %s)", entry.entry_id)

    return True
