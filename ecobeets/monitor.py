import argparse
import json
import time
import ecobeets.common as common


# TODO: use the thermostatSummary API to figure out if anything has changed
# since we last polled.
# https://www.ecobee.com/home/developer/api/documentation/v1/operations/get-thermostat-summary.shtml

class Monitor:

    def __init__(self, api, count, interval):
        self.api = api
        self.count = count
        self.forever = count is None
        self.interval = interval

    def get_current_status(self):
        body = {
            "selection": {
                "selectionType": "registered",
                "selectionMatch": "",
                "includeRuntime": True,
                "includeEquipmentStatus": True,
                "includeWeather": True,
                "includeSensors": True,
                "includeExtendedRuntime": True,
                "includeDevice": True,
                "includeEvents": True,
                "includeProgram": True
            }
        }
        return self.api.request('1/thermostat', params={
            "format": "json",
            "body": json.dumps(body),
        }, method='get', auth_needed=True)

    def run(self):
        while self.forever or self.count:
            status = self.get_current_status()
            # NOTE: status can be None if there is a failure
            print(json.dumps(status))

            if self.count:
                self.count -= 1
            if self.forever or self.count:
                time.sleep(self.interval)


def main():
    parser = argparse.ArgumentParser(description="""
    Polls the Ecobee API to get information about the current state of
    configured thermostats.
    """)

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
    api = common.ApiHelper(token_file=opts['token_file'])

    monitor = Monitor(api=api, count=opts['count'], interval=opts['interval'])
    monitor.run()
