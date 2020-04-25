import argparse
import json
import os.path
import requests
import sys
import ecobeets.common as common


def check_error_resp(resp):
    if 'error' in resp:
        print("ERROR: %s" % resp['error_description'])
        sys.exit(-1)


def register_app(api_key):
    print("Creating application registration PIN...")
    r = requests.get(common.ECOBEE_API + '/authorize', params={
        'response_type': 'ecobeePin',
        'client_id': api_key,
        'scope': 'smartRead',
    })
    auth_resp = r.json()
    check_error_resp(auth_resp)

    print("PIN created successfully: '%s'" % auth_resp['ecobeePin'])
    print("Go to https://www.ecobee.com/consumerportal/index.html")
    print("and enter this PIN in the 'My Apps' section within 10 mins.")
    input("Press Enter when done...")

    return auth_resp['code']


def get_tokens(api_key, code):
    print("Requesting access and refresh tokens...")
    r = requests.post(common.ECOBEE_API + '/token', params={
        'grant_type': 'ecobeePin',
        'client_id': api_key,
        'code': code,
    })
    token_resp = r.json()
    check_error_resp(token_resp)
    return token_resp


def write_tokens(token_file, tokens):
    print("Writing access and refresh tokens to '%s'" % token_file)
    with open(token_file, 'w') as fh:
        fh.write(json.dumps(tokens))


def main():
    parser = argparse.ArgumentParser(description="""
    Performs initial API authentication and obtains an refresh token for use 
    with the ecobeets-monitor.
    """)

    parser.add_argument('-a', '--api-key', required=True,
                        help="Ecobee API Key")

    parser.add_argument('-t', '--token-file', required=False,
                        default="~/.ecobeets",
                        help="File to store access tokens in")

    opts = vars(parser.parse_args())
    api_key = opts['api_key']
    token_file = os.path.expanduser(opts['token_file'])

    if os.path.isfile(token_file):
        print("ERROR: token file '%s' exists. Remove to force "
              "re-authorization." % token_file)
        sys.exit(1)

    print("Welcome to EcobeeTS Setup")
    code = register_app(api_key)
    tokens = get_tokens(api_key, code)
    write_tokens(token_file, tokens)

    print("Done! You can now use the ecobeets tools.")
    print("E.g., try 'ecobeets-monitor --token-file=\"%s\" -c 1" % token_file)
