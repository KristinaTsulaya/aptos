import json
import requests
import re


class Trade:
    def __init__(self, api_key, address):
        self.api_key = api_key
        self.address = address
        self.url = f'https://aptos-mainnet.nodereal.io/v1/{self.api_key}/v1/accounts/{self.address}/resources'
        self.headers = {
            'accept': 'application/json'
        }
        self.tokens = {
            'SOL': '0x881ac202b1f1e6ad4efcff7a1d0579411533f2502417a19211cfc49751ddb5f4::coin::MOJO',
            'APT': '0x1::aptos_coin::AptosCoin',
            'ALT': '0xae478ff7d83ed072dbc5e264250e67ef58f57c99d89b447efd8a0a2e8b2be76e::coin::T',
            'tAPT': '0xa2eda21a58856fda86451436513b867c97eecb4ba099da5775520e0f7492e852::coin::T',
            'USDT': '0xd0b4efb4be7c3508d9a26a9b5405cf9f860d0b9e5fe2f498b90e68b8d2cedd3e::aptos_launch_token::AptosLaunchToken',
            'WBTC': '0xcc8a89c8dce9693d354449f1f73e60e14e347417854f029db5bc8e7454008abb::coin::T',
            'WETH': '0x7fd500c11216f0fe3095d0c4b8aa4d64a4e2e04f83758462f2b127255643615::thl_coin::THL',
            'zUSDC': '0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDC',
            'zWETH': '0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::WETH',
            'zUSDT': '0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDT',
            'USDCet': '0x5e156f1207d0ebfa19a9eeff00d62a282278fb8719f4fab3a586a0a2c0fffbea::coin::T'
        }
        self.my_dict = {}
        self.resources = {}

    def get_resources(self):
        self.resp = requests.get(self.url, headers=self.headers)
        self.parse_resp()

    def parse_resp(self):
        keys = []
        counter = 0
        for i in self.resp.json():
            if 'type' in i:
                pattern = '0x[a-fA-F0-9]+::swap::TokenPairReserve<0x[a-fA-F0-9]+::[a-zA-Z_]+::[a-zA-Z]+, 0x[a-fA-F0-9]+::[a-zA-Z_]+::[a-zA-Z]+<0x[a-fA-F0-9]+::[a-zA-Z_]+::[a-zA-Z]+, 0x[a-fA-F0-9]+::[a-zA-Z_]+::[a-zA-Z]+>>|0x[a-fA-F0-9]+::swap::TokenPairReserve<0x[a-fA-F0-9]+::[a-zA-Z_]+::[a-zA-Z]+, 0x[a-fA-F0-9]+::[a-zA-Z_]+::[a-zA-Z]+>|0x[a-fA-F0-9]+::swap::TokenPairReserve<0x[a-fA-F0-9]+::[a-zA-Z]+[0-9]*::[a-zA-Z]+<0x[a-fA-F0-9]+::coin::[a-zA-Z]+, 0x[a-fA-F0-9]+::[a-zA-Z]+::[a-zA-Z]+>, 0x[a-fA-F0-9]+::[a-zA-Z_]+::[a-zA-Z]+>'
                resource_type = re.findall(pattern, json.dumps(i), flags=re.M)
                if resource_type:
                    for k, v in self.tokens.items():
                        if v in resource_type[0]:
                            counter += 1
                            keys.append(k)
                            if counter == 2:
                                inner_part = resource_type[0].split("<")[-1].split(">")[0]
                                x_coin = inner_part.split(", ")[-2]
                                y_coin = inner_part.split(', ')[-1]
                                if self.tokens[keys[0]] == x_coin:
                                    x_key = keys[0]
                                elif self.tokens[keys[0]] == y_coin:
                                    y_key = keys[0]
                                if self.tokens[keys[1]] == y_coin:
                                    y_key = keys[1]
                                elif self.tokens[keys[1]] == x_coin:
                                    x_key = keys[1]
                                self.get_resource(resource_type[0], x_key, y_key, False)

                                self.resources[f'{x_key}_{y_key}'] = resource_type[0]  # сохраняем для повторного
                                # запуска
                                break
                    counter = 0
                    keys.clear()

    def check_tokens(self, x_token, y_token):
        if f'{x_token}_{y_token}' in self.resources:
            resource_type = self.resources[f'{x_token}_{y_token}']
            pair = self.get_resource(resource_type, x_token, y_token, True)
            return pair

    def get_resource(self, resource_type, x_token, y_token, out):
        url = f"https://aptos-mainnet.nodereal.io/v1/{self.api_key}/v1/accounts/{self.address}/resource/{resource_type}"
        resp = requests.get(url, headers=self.headers)

        if 'data' in resp.json():
            self.my_dict[f'{x_token}_{y_token}'] = {'reserve_x': resp.json()['data']['reserve_x'],
                                                    'reserve_y': resp.json()['data']['reserve_y']}
            if out:
                return self.my_dict[f'{x_token}_{y_token}']

