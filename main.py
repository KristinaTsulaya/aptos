from earn_a_lot_of_money_bitch import Trade
from params import *
from flask import Flask, request
import json


app = Flask(__name__)
bot = Trade(api_key, address)
bot.get_resources()


@app.route('/get_tokens', methods=['POST'])
def receive_data():
    data = request.json()

    token1 = data["token1"]
    token2 = data["token2"]
    return json.dumps(bot.check_tokens(token1, token2))


@app.route('/all_pairs', methods=['POST'])
def all_pairs():
    return json.dumps(bot.resources.keys())


if __name__ == '__main__':
    while True:
        app.run(host='127.0.0.1', port=5000)
