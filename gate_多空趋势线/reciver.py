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
        prev_market_position = data['prev_market_position']
        symbol = data['symbol']
        port = data['port']
        if symbol not in bank:
            bank[symbol] = {
                'status_position' : -1,
                'permission' : 0,
                'port' : port
            }

            
        if direction == 'TakeProfit' and bank[symbol]['status_position'] == 1:
            print("==========TakeProfit==========")
        else:
            if prev_market_position == 'flat' and bank[symbol]['status_position'] == -1:
                bank[symbol]['permission'] = 1
            if bank[symbol]['permission'] == 1:
                bank[symbol]['status_position'] = 1
        print(f'信号接收时间 : {datetime.datetime.now()}')
        print(f'币种 : {symbol} | 开/平仓 : {direction} | 开仓张数 : {contract} | 仓位状态 : {bank[symbol]["status_position"]}')
        # if bank[symbol]['status_position'] != -1:
        try:
            response = requests.post(f'http://127.0.0.1:{port}/trade', data = request.data)
            print(f"HTTP状态 : {response.status_code}")
            print('[测试]状态正常')
        except Exception as e:
            print(f"{symbol}信号传递存在错误: {e}")
            print("仓位状态回归静止态，交易许可已取消")
            bank[symbol]['status_position'] = -1
            bank[symbol]['permission'] = 0
            print(f'币种 : {symbol} | 仓位状态 : {bank[symbol]["status_position"]} | 交易许可 : {bank[symbol]["permission"]}')
        return "success"
    except Exception as error:
        print(f"error: {error}")
        return "failure"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8888, debug=False)
