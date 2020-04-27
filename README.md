# EcobeeTS
Scripts to poll an Ecobee thermostat and write time series to a DB

## Getting Started

1. Create an application in the Developer" menu of the 
[Ecobee customer portal](https://www.ecobee.com/consumerportal/index.html). 
Take note of the "API Key" of your application.


2. Run the `ecobeets-setup` tool, providing your API Key:
```
ecobeets-setup --api-key=<mysecretkey>
```

3. Follow the prompts to associate your application with your thermostat and 
obtain authorization tokens.

## Real-time monitoring

Use the `ecobeets-monitor` tool to continuously monitor your thermostat(s)
and generate time series.

Note that you must first have run followed the setup instructions above.

#### Run once

```
ecobeets-monitor -c 1
```
This will query the API for current thermostat status and write the time series
data points to stdout in JSON format.

#### Continuously monitor and write to InfluxDB

```
ecobeets-monitor -o influxdb \
    --influx-url=http://localhost:9999 \
    --influx-token="myinfluxtoken" \
    --influx-org=MyOrg \
    --influx-bucket=my_bucket
```
This will periodically (every 5 mins) query the API for thermostat status and
write the data to the given InfluxDB.

## Known Issues

 - There doesn't seem to be any way to obtain tokens for an application that has
   already been registered. It's annoying, but re-running `ecobeets-setup`
   seems to be the only option if your refresh token expires (or you lose your
   `~/.ecobeets` config file). Note that you can re-add the same application
   without removing the previous instance (it will be overwritten).

## Planned Features

 - Extend the `ecobeets-setup` script to ask for InfluxDB configuration
   information so that this doesn't need to be provided on the command line.

 - Refactor InfluxDB code into common class so that other (planned) tools can
   easily write to Influx

 - Dockerize (better yet, k8s) a full deployment that includes EcobeeTS,
   InfluxDB, NGINX, Grafana, etc.

 - Create `ecobeets-historical` or similar to bootstrap the database with
   historical data available via the Ecobee API.
