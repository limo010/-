# 测试是否正常接收tv消息
import requests
import json
data = {'ticker': 'CFXUSDT.P', 'ex': 'BINANCE', 'close': '0.1857', 'open': '0.1853', 'high': '0.1857', 'low': '0.1852', 'time': '2023-07-07T21:00:00Z', 'volume': '1525695', 'interval': '10', 'position_size': '0', 'action': 'sell', 'contracts': '13.262', 'price': '0.1857', 'market_position': 'flat', 'market_position_size': '0', 'prev_market_position': 'long', 'prev_market_position_size': '13.262', 'action2': 'TakeProfit', 'port': '7795', 'symbol': 'CFXUSDT'}
# data = {'ticker': 'CFXUSDT.P', 'ex': 'BINANCE', 'close': '0.1887', 'open': '0.1893', 'high': '0.1897', 'low': '0.1887', 'time': '20231-07-08T03:30:00Z', 'volume': '4067437', 'interval': '10', 'position_size': '333.737', 'action': 'buy', 'contracts': '30', 'price': '0.177', 'market_position': 'long', 'market_position_size': '33.737', 'prev_market_position': 'flat', 'prev_market_position_size': '0', 'action2': 'Long1', 'port': '7795', 'symbol': 'CFXUSDT'}
data = json.dumps(data)
response = requests.post(f'http://43.134.193.86/webhook', data = data)
print(response)
