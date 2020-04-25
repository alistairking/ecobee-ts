import os.path
import json
import requests
import sys
import time

ECOBEE_API = "https://api.ecobee.com"
ECOBEETS_CONFIG = "~/.ecobeets"


class ApiHelper:

    def __init__(self, token_file=ECOBEETS_CONFIG, skip_validation=False):
        self.token_file = os.path.expanduser(token_file)
        self.tokens = None
        self.last_refresh = 0

        if skip_validation:
            return

        if not os.path.isfile(self.token_file):
            raise ValueError("Token file '%s' does not exist. Perhaps you "
                             "haven't run ecobeets-setup yet." %
                             self.token_file)
        self.load_tokens()

    def load_tokens(self):
        with open(self.token_file) as tf:
            self.tokens = json.loads(tf.read())
        if 'refresh_time' in self.tokens:
            self.last_refresh = self.tokens['refresh_time']
        self.maybe_refresh_tokens()

    def write_tokens(self):
        with open(self.token_file, 'w') as fh:
            fh.write(json.dumps(self.tokens))

    def maybe_refresh_tokens(self, force_refresh=False):
        now = time.time()
        expired = (self.last_refresh + self.tokens['expires_in']) < now
        if not (expired or force_refresh):
            return
        refresh_resp = self.request(endpoint='token', params={
            'grant_type': 'refresh_token',
            'refresh_token': self.tokens['refresh_token'],
            'client_id': self.tokens['api_key'],
        }, method='post')
        refresh_resp['api_key'] = self.tokens['api_key']
        refresh_resp['refresh_time'] = now
        self.tokens = refresh_resp
        self.last_refresh = now
        self.write_tokens()

    def request(self, endpoint, params, method='get', auth_needed=False):
        funcs = {'get': requests.get, 'post': requests.post}
        headers = {}
        if auth_needed:
            self.maybe_refresh_tokens()
            headers["Authorization"] = "Bearer %s" % self.tokens['access_token']
        r = funcs[method](ECOBEE_API + '/' + endpoint,
                          params=params,
                          headers=headers)
        resp = r.json()
        if 'error' in resp:
            raise ValueError(resp['error_description'])
        if 'status' in resp and resp['status']['code']:
            sys.stderr.write("WARN: non-zero status code: %s\n" % resp[
                'status']['message'])
            return None
        return resp
