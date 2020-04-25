import dateutil.parser

"""
Parses a "Thermostat" object an extracts a set of InfluxDB-compatible data
points.
"""


class Thermostat:

    def __init__(self, api_data):
        self.tags = {}

        self.parse_api_data(api_data)

    def add_tag(self, tag, value):
        self.tags[tag] = value

    def parse_date(self, datestr, is_utc):
        dt = dateutil.parser.parse(datestr, ignoretz=is_utc)
        return dt

    def parse_api_data(self, api_data):
        """
        Parses top-level thermostat information.

        {
          "identifier": "412856756309",
          "name": "KingTemp",
          "thermostatRev": "200425225616",
          "isRegistered": true,
          "modelNumber": "nikeSmart",
          "brand": "ecobee",
          "features": "Home,HomeKit",
          "lastModified": "2020-04-25 22:56:16",
          "thermostatTime": "2020-04-25 16:03:20",
          "utcTime": "2020-04-25 23:03:20",
          "runtime": ...,
          "extendedRuntime": ...,
          "equipmentStatus": ...,
          "remoteSensors": ...,
        }
        """
        # global tags that will be applied to all thermostat measurements
        self.add_tag('identifier', api_data['identifier'])
        self.add_tag('name', api_data['name'])
        self.add_tag('revision', api_data['thermostatRev'])
        self.add_tag('registered', api_data['isRegistered'])
        self.add_tag('model', api_data['modelNumber'])
        self.add_tag('brand', api_data['brand'])
