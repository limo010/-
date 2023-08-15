import requests
import json
data = {'ticker': 'XRPUSDT.P', 'ex': 'BINANCE', 'close': '0.1857', 'open': '0.1853', 'high': '0.1857', 'low': '0.1852', 'time': '2023-07-07T21:00:00Z', 'volume': '1525695', 'interval': '10', 'position_size': '0', 'action': 'sell', 'contracts': '500.262', 'price': '0.1857', 'market_position': 'flat', 'market_position_size': '0', 'prev_market_position': 'long', 'prev_market_position_size': '13.262', 'action2': 'TakeProfit', 'port': '77', 'symbol': 'XRPUSDT'}
# data = {'ticker': 'XRPUSDT.P', 'ex': 'BINANCE', 'close': '0.1887', 'open': '0.1893', 'high': '0.1897', 'low': '0.1887', 'time': '2023-07-08T03:30:00Z', 'volume': '4067437', 'interval': '10', 'position_size': '333.737', 'action': 'buy', 'contracts': '30', 'price': '0.7513', 'market_position': 'long', 'market_position_size': '33.737', 'prev_market_position': 'flat', 'prev_market_position_size': '0', 'action2': 'Long2', 'port': '7793', 'symbol': 'XRPUSDT'}
data = json.dumps(data)
response = requests.post(f'http://43.156.32.130/webhook', data = data)
print(response)