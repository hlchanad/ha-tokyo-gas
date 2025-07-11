# TokyoGas Scraper for Home Assistant

Scrape electricity usage data from TokyoGas at 14:00 every day. It integrates 
into Home Assistant by addon and custom component. You may add the scraped 
statistics to the Energy dashboard.

![energy-dashboard](assets/energy-dashboard.png)
![tokyo-gas-dashboard](assets/tokyo-gas-dashboard.png)

> [!WARNING]
> This is still **under construction**. It might be unstable and use it on your
> own risk.

> [!WARNING]
> This is the first time I write Python and extend Home Assistant. The code might
> not be ideal.

## Installation

### Addon

1. Copy the whole `/addon` folder to `/addons/local/tokyo-gas-scraper` in your Home Assistant 
   instance
2. Restart the Home Assistant instance
3. Navigate to `Settings` > `Add-ons` > `Add-on Store` 

   ![addon-store](assets/addon-store.png)
4. Install the addon
5. By default, the server will be hosted at http://homeassistant.local:8000. 
   But you can also update the port in the Configuration tab.

### Custom Component

1. Copy the whole `/custom_component` folder to 
   `/config/custom_components/tokyo_gas` in your Home Assistant instance
2. Restart the Home Assistant instance
3. Navigate to `Settings` > `Devices & services` > `Add Integration`

   ![add-integration](assets/add-integration.png)
4. Fill in the login credentials and the domain if you updated the setting

## Usage

After installing the addon and custom component as mentioned above, the data
will be scraped for you automatically at next 14:00 (by default). In case 
there are quite a few integrations, and it might be confusing which statistic
ID should be used, the targeted statistic ID could be viewed in the service.

![tokyo-gas-service](assets/tokyo-gas-service.png)
![statistic-id](assets/statistic-id.png)

### Custom Service

A custom service could be triggered to fetch and insert the statistics manually.
It would be useful when somehow the data could not be fetched. 

Note that the cumulative sum of the latter records should be fixed afterward.

```yaml
action: tokyo_gas.fetch_electricity_usage
data:
  # number of days in the past
  delta_days: 3 
  # the entity id of the sensor by this integration
  statistic: sensor.foobar_electricity_usage_stat_id
```

![service.png](assets/service.png)

## Known Issues

The scraper occasionally fails to scrape because of timeout in playwright. 
There might be some funny handling in the TokyoGas website that I am not 
aware of. If the CPU/ memory of the addon goes high, restart it and run the 
custom service to fill the gaps.

## Up-coming plans

- Support options modification for custom component after initialization
- Write test cases for all files
- Support multiple customer number in one account
