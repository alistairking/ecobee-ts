from setuptools import setup

setup(
    name='ecobeets',
    version='0.1',
    packages=['ecobeets'],
    url='https://github.com/alistairking/ecobee-ts',
    license='MIT',
    author='Alistair King',
    author_email='alistair@kiwimaple.com',
    description='Scripts to poll an Ecobee thermostat and write time series '
                'to InfluxDB',
    install_requires=[
        'requests',
        'influxdb-client',
        'python-dateutil',
    ],
    entry_points={'console_scripts': [
        'ecobeets-monitor = ecobeets.monitor:main',
        'ecobeets-setup = ecobeets.setup:main',
    ]},
)
