from setuptools import setup

setup(
    name='ecobee-ts',
    version='0.1',
    packages=['ecobeets'],
    url='https://github.com/alistairking/ecobee-ts',
    license='MIT',
    author='Alistair King',
    author_email='alistair@kiwimaple.com',
    description='Scripts to poll an Ecobee thermostat and write time series to a DB',
    install_requires=[
        'requests',
    ],
    entry_points={'console_scripts': [
        'ecobeets-monitor = ecobeets.monitor:main',
        'ecobeets-setup = ecobeets.setup:main',
    ]},
)
