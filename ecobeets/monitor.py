import argparse
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import json
import logging
import time
import ecobeets.common as common
import ecobeets.parsers as parsers

# TODO: better logging setup etc.
logging.getLogger().setLevel("INFO")

# TODO: use the thermostatSummary API to figure out if anything has changed
# since we last polled.
# https://www.ecobee.com/home/developer/api/documentation/v1/operations/get-thermostat-summary.shtml

class Monitor:

    def __init__(self, token_file, count, interval, output_type,
                 influx_url, influx_token, influx_org, influx_bucket):
        self.api = common.ApiHelper(token_file)
        self.count = count
        self.forever = count is None
        self.interval = interval
        self.outtype = output_type
        if output_type == "influxdb":
            # init influx client
            self.influx = InfluxDBClient(
                url=influx_url,
                token=influx_token,
                org=influx_org
            )
            self.influx_writer = \
                self.influx.write_api(write_options=SYNCHRONOUS)
            self.influx_org = influx_org
            self.influx_bucket = influx_bucket

    def influx_write(self, data):
        self.influx_writer.write(self.influx_bucket, self.influx_org, data)

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
            logging.info("Polling thermostat API")
            # TODO: use thermostatSummary to figure out what has changed
            for td in self.get_thermostats():
                therm = parsers.Thermostat(td)
                if self.outtype == "json":
                    print(json.dumps(therm.points, default=str))
                else:
                    assert(self.outtype == "influxdb")
                    self.influx_write(therm.points)

            if self.count:
                self.count -= 1
            if self.forever or self.count:
                time.sleep(self.interval)
        self.influx_writer.__del__()
        self.influx.__del__()


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

    parser.add_argument('-u', '--influx-url', required=False,
                        default="http://localhost:9999",
                        help="InfluxDB Url")

    parser.add_argument('-k', '--influx-token', required=False,
                        help="InfluxDB Token")

    parser.add_argument('-r', '--influx-org', required=False,
                        help="InfluxDB Org")

    parser.add_argument('-b', '--influx-bucket', required=False,
                        help="InfluxDB Bucket")

    opts = vars(parser.parse_args())
    monitor = Monitor(**opts)
    monitor.run()
