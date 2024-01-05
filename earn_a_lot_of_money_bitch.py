import json
import requests
import re

class Trade:
    def __init__(self, api_key, address):
        self.api_key = api_key
        self.address = address
        self.url = f'https://aptos-mainnet.nodereal.io/v1/{self.api_key}/v1/accounts/{self.address}/resources'
        self.headers = {
            "accept": "application/json"
        }
        self.position = 0
        self.my_dict = {}

    def get_resources(self):
        self.resp = requests.get(self.url, headers=self.headers)
        self.parse_resp()

    def parse_resp(self):
        for i in self.resp.json():
            if 'type' in i:
                pattern = '0x[a-fA-F0-9]+::swap::TokenPairReserve<0x[a-fA-F0-9]+::[a-zA-Z_]+::[a-zA-Z]+, 0x[a-fA-F0-9]+::[a-zA-Z_]+::[a-zA-Z]+<0x[a-fA-F0-9]+::[a-zA-Z_]+::[a-zA-Z]+, 0x[a-fA-F0-9]+::[a-zA-Z_]+::[a-zA-Z]+>>|0x[a-fA-F0-9]+::swap::TokenPairReserve<0x[a-fA-F0-9]+::[a-zA-Z_]+::[a-zA-Z]+, 0x[a-fA-F0-9]+::[a-zA-Z_]+::[a-zA-Z]+>|0x[a-fA-F0-9]+::swap::TokenPairReserve<0x[a-fA-F0-9]+::[a-zA-Z]+[0-9]*::[a-zA-Z]+<0x[a-fA-F0-9]+::coin::[a-zA-Z]+, 0x[a-fA-F0-9]+::[a-zA-Z]+::[a-zA-Z]+>, 0x[a-fA-F0-9]+::[a-zA-Z_]+::[a-zA-Z]+>'
                resource_type = re.findall(pattern, json.dumps(i), flags=re.M)
                if resource_type:
                    self.get_resource(resource_type)
        print(self.my_dict)

    def get_resource(self, resource_type):
        url = f"https://aptos-mainnet.nodereal.io/v1/{self.api_key}/v1/accounts/{self.address}/resource/{resource_type}"
        resp = requests.get(url, headers=self.headers)
        print(resp.json())

        if 'data' in resp.json():
            self.my_dict[self.position] = {'reserve_x': resp.json()['data']['reserve_x'], 'reserve_y': resp.json()['data']['reserve_y']}
            self.position += 1

#todo:
# 1) refactor the pattern
# 2) check the resource type str