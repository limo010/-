import requests
import json
import time
from json_create import save_data
import threading
json_name = "成交量策略日志.json"

# 输入毫秒级的时间，转出正常格式的时间
def timeStamp(timeNum):
    timeStamp = float(timeNum/1000)
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    # print (otherStyleTime)
    return otherStyleTime

proxies = {
    'http': 'http://127.0.0.1:33210',
    'https': 'http://127.0.0.1:33210'
}

url = 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=50'
while 1:
    time.sleep(1)
    response = requests.get(url, proxies=proxies)
    data = response.json()
    print('数据长度', len(data[0:48]))
    sum = 0
    i = 0
    for value in data[0:48]:
        if float(value[4]) > float(value[1]):
            print('K线开盘时间', timeStamp(value[0]), '成交量', value[5], 'K线收盘时间', timeStamp(value[6]), '收盘价', value[4], '价格上涨')
        else:
            print('K线开盘时间', timeStamp(value[0]), '成交量', value[5], 'K线收盘时间', timeStamp(value[6]), '收盘价', value[4], '价格下跌')
        sum = sum + float(value[5])
    if float(data[49][4]) > float(data[49][1]):
        print('K线开盘时间', timeStamp(data[49][0]), '成交量', data[49][5], 'K线收盘时间', timeStamp(data[49][6]), '收盘价', data[49][4],'价格上涨')
    else:
        print('K线开盘时间', timeStamp(data[49][0]), '成交量', data[49][5], 'K线收盘时间', timeStamp(data[49][6]), '收盘价', data[49][4],'价格下跌')
    print('50根K柱的总成交量', sum, '平均值', sum/49)

    # 当前这个时间段的成交额大于50个K柱的成交额平均值
    if float(data[49][5]) > sum / 49:
        print('超出平均值')
        # 开多
        if float(data[49][4]) > float(data[49][1]):
            print('开多')
            temp = {}
            temp['open'] = '开多'
            temp['开盘时间'] = str(timeStamp(data[49][6]))
            temp['开仓时间'] = time.strftime('%Y-%m-%d %H:%M:%S')
            temp['最新价'] = str(data[49][4])
        # 开空
        else:
            print('开空')
            temp = {}
            temp['open'] = '开空'
            temp['开盘时间'] = str(timeStamp(data[49][6]))
            temp['开仓时间'] = time.strftime('%Y-%m-%d %H:%M:%S')
            temp['最新价'] = str(data[49][4])
        # 保存数据
        t1 = threading.Thread(target=save_data, args=(temp, json_name))
        t1.start()
        # 三秒后平仓
        time.sleep(3)
        url_close = 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=1'
        response = requests.get(url_close, proxies=proxies)
        data = response.json()
        temp = {}
        temp['open'] = '平仓'
        temp['平仓时间'] = time.strftime('%Y-%m-%d %H:%M:%S')
        temp['最新价'] = str(data[0][4])
        # 保存数据
        t1 = threading.Thread(target=save_data, args=(temp, json_name))
        t1.start()




