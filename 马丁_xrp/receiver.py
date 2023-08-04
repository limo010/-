import json
import datetime
import requests
from flask import Flask, request

app = Flask(__name__)
bank = {}

@app.route('/webhook', methods=['POST'])
def webhook():
    global bank
    try:
        data = json.loads(request.data)
        print(data)
        direction = data['action2']
        contract = data['contracts']
        symbol = data['symbol']
        port = data['port']
        print(f'信号接收时间 : {datetime.datetime.now()}')
        print(f'币种 : {symbol} | 开/平仓 : {direction} | 开仓张数 : {contract}')
        try:
            response = requests.post(f'http://127.0.0.1:{port}/webhook', data = request.data)
            print(f"HTTP状态 : {response.status_code}")
            print('[测试]状态正常')
        except Exception as e:
            print(e)
        return "success"
    except Exception as error:
        print(f"error: {error}")
        return "failure"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8888, debug=False)
