import dateutil.parser
import datetime

"""
Parses a "Thermostat" object an extracts a set of InfluxDB-compatible data
points.
"""


class Thermostat:

    def __init__(self, api_data):
        self.global_tags = {}
        self.points = []
        self.utc_time = None

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

    @staticmethod
    def parse_date(datestr):
        return dateutil.parser.parse(datestr, ignoretz=True)

    def compute_delta(self, datestr):
        p = self.parse_date(datestr)
        return (self.utc_time - p).total_seconds()

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
        self.utc_time = self.parse_date(api_data['utcTime'])

        self.add_point(
            measurement='thermostat_summary',
            fields={
                'config_mod_delta': self.compute_delta(api_data['lastModified'])
            },
            time=self.utc_time)

        # parse sub-objects
        if 'runTime' in api_data:
            self.parse_runtime(api_data['runtime'])
        if 'extendedRuntime' in api_data:
            self.parse_ext_runtime(api_data['extendedRuntime'])
        if 'remoteSensors' in api_data:
            self.parse_remote_sensors(api_data['remoteSensors'])

    def parse_runtime(self, rt):
        """
        Parses runtime data
        {
          "runtimeRev": "200425230039",
          "connected": true,
          "firstConnected": "2019-12-18 02:49:15",
          "connectDateTime": "2020-04-25 18:58:52",
          "disconnectDateTime": "2020-04-25 18:44:40",
          "lastModified": "2020-04-25 23:00:39",
          "lastStatusModified": "2020-04-25 23:00:39",
          "runtimeDate": "2020-04-25",
          "runtimeInterval": 273,
          "actualTemperature": 780,
          "actualHumidity": 50,
          "rawTemperature": 780,
          "showIconMode": 0,
          "desiredHeat": 600,
          "desiredCool": 820,
          "desiredHumidity": 36,
          "desiredDehumidity": 60,
          "desiredFanMode": "auto",
          "desiredHeatRange": [450, 790],
          "desiredCoolRange": [650, 920]
        }
        """
        fields = {
            'runtime_revision': rt['runtimeRev'],  # opaque id
            'connected': rt['connected'],  # bool

            # elapsed times since something happened
            'first_connected_delta': self.compute_delta(rt['firstConnected']),
            'last_disconnect_delta': self.compute_delta(rt['disconnectDateTime']),
            'last_connect_delta': self.compute_delta(rt['connectDateTime']),
            'update_delta': self.compute_delta(rt['lastModified']),
            'status_update_delta': self.compute_delta(rt['lastStatusModified']),

            # environmental readings are taken from extended runtime object
        }

        self.add_point(
            measurement='thermostat_summary',
            fields=fields,
            time=self.utc_time
        )

    def parse_ext_runtime(self, ert):
        """
        Parses extended runtime data

        From what I understand, the thermostat reports 5-minute granularity data
        every 15 minutes. The extended runtime data thus includes three data
        points (lRT, lRT-5, lRT-10).
        {
          "lastReadingTimestamp": "2020-04-25 22:45:00",
          "runtimeDate": "2020-04-25",
          "runtimeInterval": 273,
          "actualTemperature": [798, 793, 787],
          "actualHumidity": [50, 49, 48],
          "desiredHeat": [600, 600, 600],
          "desiredCool": [780, 780, 780 ],
          "desiredHumidity": [0, 0, 0],
          "desiredDehumidity": [0, 0, 0],
          "dmOffset": [0, 0, 0],
          "hvacMode": [
            "compressorCoolStage1On",
            "compressorCoolStage1On",
            "compressorCoolStage1On"
          ],
          "heatPump1": [0, 0, 0],
          "heatPump2": [0, 0, 0],
          "auxHeat1": [0, 0, 0],
          "auxHeat2": [0, 0, 0],
          "auxHeat3": [0, 0, 0],
          "cool1": [300, 300, 300],
          "cool2": [0, 0, 0],
          "fan": [300, 300, 300],
          "humidifier": [0, 0, 0],
          "dehumidifier": [0, 0, 0],
          "economizer": [0, 0, 0],
          "ventilator": [0, 0, 0],
          "currentElectricityBill": 0,
          "projectedElectricityBill": 0
        }
        """
        # better make a copy since we're going to mangle it
        ert = ert.copy()

        # lrt is the time of reading[2]
        lrt = self.parse_date(ert['lastReadingTimestamp'])

        del ert['lastReadingTimestamp']
        del ert['runtimeDate']
        del ert['runtimeInterval']

        # TODO: parse current and projected electricity bill figures
        del ert['currentElectricityBill']
        del ert['projectedElectricityBill']

        # temperatures are in F multiplied by 10: 72.1 -> 720
        temp_fields = {
            'actualTemperature': 'temperature',
            'desiredHeat': 'desired_heat',
            'desiredCool': 'desired_cool',
            'dmOffset': 'demand_offset_temp',
        }

        # explicit integer fields
        int_fields = {
            'actualHumidity': 'actual_humidity',
            'desiredHumidity': 'desired_humidity',
            'desiredDehumidity': 'desired_dehumidity',
        }

        string_fields = {
            'hvacMode': 'hvac_mode',
        }

        # runtime fields (in seconds)
        # these will become 'runtime_##name' (all lowercase)
        runtime_fields = [
            'heatPump1',
            'heatPump2',
            'auxHeat1',
            'auxHeat2',
            'auxHeat3',
            'cool1',
            'cool2',
            'fan',
            'humidifier',
            'dehumidifier',
            'economizer',
            'ventilator'
        ]

        # fields at lrt-10, lrt-5, lrt
        env_points = [{}, {}, {}]
        equip_points = [{}, {}, {}]
        for field in ert.keys():
            for i, val in enumerate(ert[field]):
                if field in temp_fields:
                    env_points[i][temp_fields[field]] = val/10
                elif field in int_fields:
                    env_points[i][int_fields[field]] = val
                elif field in runtime_fields:
                    fname = "runtime_%s" % field.lower()
                    equip_points[i][fname] = val
                else:
                    assert(field in string_fields)
                    env_points[i][string_fields[field]] = val

        intvl = datetime.timedelta(minutes=5)
        for i, ts in enumerate([lrt-(intvl*2), lrt-intvl, lrt]):
            self.add_point(
                measurement='thermostat_environment',
                fields=env_points[i],
                time=ts
            )
            self.add_point(
                measurement='thermostat_equipment',
                fields=equip_points[i],
                time=ts
            )

    def parse_remote_sensors(self, es):
        pass
