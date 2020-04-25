# ecobee-ts
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

## Known Issues

- There doesn't seem to be any way to obtain tokens for an application that has
 already been registered. It's annoying, but re-running `ecobeets-setup` 
 seems to be the only option if your refresh token expires (or you lose your
  `~/.ecobeets` config file). Note that you can re-add the same application
  without removing the previous instance (it will be overwritten).