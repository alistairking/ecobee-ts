import argparse
import json
import time
import ecobeets.common as common
import ecobeets.parsers as parsers


# TODO: use the thermostatSummary API to figure out if anything has changed
# since we last polled.
# https://www.ecobee.com/home/developer/api/documentation/v1/operations/get-thermostat-summary.shtml

class Monitor:

    def __init__(self, token_file, count, interval, output_type):
        self.api = common.ApiHelper(token_file)
        self.count = count
        self.forever = count is None
        self.interval = interval
        self.outtype = output_type

    def get_thermostats(self):
        body = {
            "selection": {
                "selectionType": "registered",
                "selectionMatch": "",
                "includeRuntime": True,
                "includeExtendedRuntime": True,
                "includeSensors": True,

                # TODO: figure out which of these are useful and create parsers
                "includeEquipmentStatus": False,
                "includeEvents": False,
                "includeDevice": False,
                "includeWeather": False,
                "includeProgram": False,
            }
        }
        resp = self.api.request('1/thermostat', params={
            "format": "json",
            "body": json.dumps(body),
        }, method='get', auth_needed=True)
        if 'page' in resp and resp['page']['totalPages'] != 1:
            raise NotImplementedError("Multi-page responses are not yet "
                                      "handled.")
        return resp['thermostatList']

    def run(self):
        while self.forever or self.count:
            # TODO: use thermostatSummary to figure out what has changed
            for td in self.get_thermostats():
                therm = parsers.Thermostat(td)
                if self.outtype == "json":
                    print(json.dumps(therm.points, default=str))
                else:
                    assert(self.outtype == "influxdb")
                    raise NotImplementedError("TODO Influxdb")

            if self.count:
                self.count -= 1
            if self.forever or self.count:
                time.sleep(self.interval)


def main():
    parser = argparse.ArgumentParser(description="""
    Polls the Ecobee API to get information about the current state of
    configured thermostats.
    """)

    parser.add_argument('-o', '--output-type', required=False,
                        default="json", choices=["json", "influxdb"],
                        help="Output format")

    parser.add_argument('-t', '--token-file', required=False,
                        default=common.ECOBEETS_CONFIG,
                        help="File to store access tokens in")

    parser.add_argument('-c', '--count', required=False,
                        default=None, type=int,
                        help="Number of data points to collect")

    parser.add_argument('-i', '--interval', required=False,
                        default=300, type=int,
                        help="Data collection interval in seconds")

    opts = vars(parser.parse_args())
    monitor = Monitor(**opts)
    monitor.run()
