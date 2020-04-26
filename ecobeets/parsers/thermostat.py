import dateutil.parser

"""
Parses a "Thermostat" object an extracts a set of InfluxDB-compatible data
points.
"""


class Thermostat:

    def __init__(self, api_data):
        self.global_tags = {}
        self.points = []

        self.parse_api_data(api_data)

    def add_tag(self, tag, value):
        self.global_tags[tag] = value

    def add_point(self, measurement, fields, time, tags=None):
        lt = self.global_tags.copy()
        if tags:
            lt.update(tags)
        self.points.append({
            'measurement': measurement,
            'tags': lt,
            'fields': fields,
            'time': time
        })

    def parse_date(self, datestr):
        return dateutil.parser.parse(datestr, ignoretz=True)

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

        # NOTE: therm_time is in an unknown time zone
        # We could probably compute the thermostat time zone by diffing against
        # utc_time
        # therm_time = self.parse_date(api_data['thermostatTime'])
        utc_time = self.parse_date(api_data['utcTime'])

        last_mod_time = self.parse_date(api_data['lastModified'])
        last_mod_dt = utc_time - last_mod_time
        self.add_point(measurement='thermostat_summary',
                       fields={'last_mod_delta': last_mod_dt.total_seconds()},
                       time=utc_time)

        # parse sub-objects
        if 'runTime' in api_data:
            self.parse_runtime(api_data['runtime'])
        if 'extendedRuntime' in api_data:
            self.parse_ext_runtime(api_data['extendedRuntime'])
        if 'equipmentStatus' in api_data:
            self.parse_equip_status(api_data['equipmentStatus'])
        if 'remoteSensors' in api_data:
            self.parse_remote_sensors(api_data['remoteSensors'])

    def parse_runtime(self, rt):
        pass

    def parse_ext_runtime(self, ert):
        pass

    def parse_equip_status(self, es):
        pass

    def parse_remote_sensors(self, es):
        pass
