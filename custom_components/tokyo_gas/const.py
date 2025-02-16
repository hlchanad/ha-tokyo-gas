from homeassistant.const import Platform

DOMAIN = "tokyo_gas"

PLATFORMS = [Platform.SENSOR]

CONF_CUSTOMER_NUMBER = "customer_number"
CONF_STAT_LABEL_ELECTRICITY_USAGE = "electricity_usage_label"

STAT_ELECTRICITY_USAGE = "electricity_usage"
