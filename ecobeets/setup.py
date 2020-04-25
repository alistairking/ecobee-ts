import argparse
import json
import os.path
import requests
import sys
import ecobeets.common as common


def register_app(api, api_key):
    print("Creating application registration PIN...")
    auth_resp = api.request('authorize', params={
        'response_type': 'ecobeePin',
        'client_id': api_key,
        'scope': 'smartRead',
    })

    print("PIN created successfully: '%s'" % auth_resp['ecobeePin'])
    print("Go to https://www.ecobee.com/consumerportal/index.html")
    print("and enter this PIN in the 'My Apps' section within 10 mins.")
    input("Press Enter when done...")

    return auth_resp['code']


def get_initial_tokens(api, api_key, code):
    print("Requesting access and refresh tokens...")
    return api.request('token', params={
        'grant_type': 'ecobeePin',
        'client_id': api_key,
        'code': code,
    }, method='post')


def main():
    parser = argparse.ArgumentParser(description="""
    Performs initial API authentication and obtains an refresh token for use 
    with the ecobeets-monitor.
    """)

    parser.add_argument('-a', '--api-key', required=True,
                        help="Ecobee API Key")

    parser.add_argument('-t', '--token-file', required=False,
                        default=common.ECOBEETS_CONFIG,
                        help="File to store access tokens in")

    opts = vars(parser.parse_args())
    api_key = opts['api_key']

    api = common.ApiHelper(token_file=opts['token_file'])

    if os.path.isfile(api.token_file):
        print("ERROR: token file '%s' exists. Remove to force "
              "re-authorization." % api.token_file)
        sys.exit(1)

    print("Welcome to EcobeeTS Setup")
    code = register_app(api, api_key)
    # we're kinda abusing the ApiHelper here, but we have to bootstrap things
    api.tokens = get_initial_tokens(api, api_key, code)
    api.tokens['api_key'] = api_key
    print("Writing access and refresh tokens to '%s'" % api.token_file)
    api.write_tokens()

    print("Done! You can now use the ecobeets tools.")
    print("E.g., try 'ecobeets-monitor --token-file=\"%s\" -c 1" %
          api.token_file)
