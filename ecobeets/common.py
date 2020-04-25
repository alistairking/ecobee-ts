import os.path
import json
import requests
import time

ECOBEE_API = "https://api.ecobee.com"
ECOBEETS_CONFIG = "~/.ecobeets"


class ApiHelper:

    def __init__(self, token_file=ECOBEETS_CONFIG):
        self.token_file = os.path.expanduser(token_file)
        self.tokens = None
        self.last_refresh = None

    def load_tokens(self):
        with open(self.token_file) as tf:
            self.tokens = json.loads(tf.read())
        self.maybe_refresh_tokens()

    def write_tokens(self):
        with open(self.token_file, 'w') as fh:
            fh.write(json.dumps(self.tokens))

    def maybe_refresh_tokens(self, force_refresh=False):
        now = time.time()
        expired = (self.last_refresh + self.tokens['expires_in']) < now
        if self.last_refresh and not (expired or force_refresh):
            return
        refresh_resp = self.request(endpoint='token', params={
            'grant_type': 'refresh_token',
            'refresh_token': self.tokens['refresh_token'],
            'client_id': self.tokens['api_key'],
        })
        refresh_resp['api_key'] = self.tokens['api_key']
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
        return resp