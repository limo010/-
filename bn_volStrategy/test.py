import time
import requests
# 三秒后平仓
time.sleep(3)
proxies = {
    'http': 'http://127.0.0.1:33210',
    'https': 'http://127.0.0.1:33210'
}

def timeStamp(timeNum):
    timeStamp = float(timeNum/1000)
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    # print (otherStyleTime)
    return otherStyleTime

while 1:
    url_close = 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=1'
    response = requests.get(url_close, proxies=proxies)
    data = response.json()
    print(data)
    print('K线开盘时间', timeStamp(data[0][0]), '成交量', data[0][5], 'K线收盘时间', timeStamp(data[0][6]), '收盘价', data[0][4])
    print('数据长度', len(data[0:48]))