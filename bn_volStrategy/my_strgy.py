import requests
import json
import numpy as np
import time
from json_create import save_data
import threading
import os

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

url = 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=100'
flag = 0
open_time = ""
duocang = 0
kongcang = 0
strtime = time.strftime('%Y:%m:%d:%H:%M:%S', time.localtime())
time_temp = str(strtime).split(":")[3]
while 1:
    time.sleep(0.5)
    try:
        response = requests.get(url, proxies=proxies)
        data = response.json()
    except:
        continue
    # 除去异常点
    List_data_erorr = []
    for value in data:
        List_data_erorr.append(float(value[5]))
    # print(List_data_erorr)
    # 计算出均值
    mean = np.mean(List_data_erorr)
    # 计算出标准差
    std = np.std(List_data_erorr)
    print('原始数据:', '数据长度', len(data), '平均值', mean, '标准差', std)
    print()
    if float(data[-1][4]) > float(data[-1][1]):
        print('开盘时间', timeStamp(data[-1][0]), '开盘价', data[-1][1], '收盘价', data[-1][4], '成交量', data[-1][5], '收盘时间', timeStamp(data[-1][6]), '主动买入成交量',data[-1][9], '价格上涨')
    else:
        print('开盘时间', timeStamp(data[-1][0]), '开盘价', data[-1][1], '收盘价', data[-1][4], '成交量', data[-1][5], '收盘时间', timeStamp(data[-1][6]), '主动买入成交量',data[-1][9], '价格下跌')
    print()
    threshold = 1  # 设定阈值为1.2倍标准差
    List_data_checked = [x for x in List_data_erorr if (x > mean - threshold * std)]
    List_data_checked = [x for x in List_data_checked if (x < mean + threshold * std)]
    # 预处理后的平均值
    mean_checked = np.mean(List_data_checked)
    # 预处理后的总成交量
    sum = np.sum(List_data_checked)
    print('预处理后:', '数据长度', len(List_data_checked), '总成交量', sum, '平均值', mean_checked)
    print()

    # 当前这个时间段的成交额大于50个K柱的成交额平均值
    if flag == 0:
        if float(data[-1][5]) > mean_checked:
            # 开多 用成交量判断方向
            if float(data[-1][4]) > float(data[-1][1]):
                print('开多')
                temp = {}
                temp['open'] = '开多'
                temp['开盘时间'] = str(timeStamp(data[-1][0]))
                temp['开仓时间'] = time.strftime('%Y-%m-%d %H:%M:%S')
                temp['最新价'] = str(data[-1][4])
                temp['成交量'] = data[-1][5]
                temp['平均值'] = mean_checked
                # 记录开盘时间
                open_time = str(timeStamp(data[-1][0]))
                flag = 1
                duocang = 1
            # 开空
            else:
                print('开空')
                temp = {}
                temp['open'] = '开空'
                temp['开盘时间'] = str(timeStamp(data[-1][0]))
                temp['开仓时间'] = time.strftime('%Y-%m-%d %H:%M:%S')
                temp['最新价'] = str(data[-1][4])
                temp['成交量'] = data[-1][5]
                temp['平均值'] = mean_checked
                # 记录开盘时间
                open_time = str(timeStamp(data[-1][0]))
                flag = 1
                kongcang = 1
            # 保存数据
            t1 = threading.Thread(target=save_data, args=(temp, json_name))
            t1.start()

    else:
        # 下一个K柱
        if str(timeStamp(data[-1][0])) != open_time:
            # 平多
            if duocang == 1:
                # 当前K柱最新价小于上一根K柱收盘价  平仓
                if data[-1][4] < data[-2][1]:
                    print("平多")
                    duocang = 0
                    flag = 0
                    open_time = ""
                    open_temp = "平多"
            # 平空
            if kongcang == 1:
                # 当前K柱最新价大于上一根K柱收盘价 平仓
                if data[-1][4] > data[-2][1]:
                    print("平空")
                    kongcang = 0
                    flag = 0
                    open_time = ""
                    open_temp = "平空"

            # 保存数据
            if flag == 0:
                temp = {}
                temp['open'] = open_temp
                temp['开盘时间'] = str(timeStamp(data[-1][0]))
                temp['平仓时间'] = time.strftime('%Y-%m-%d %H:%M:%S')
                temp['最新价'] = str(data[-1][4])
                temp['成交量'] = data[-1][5]
                temp['平均值'] = mean_checked
                # 保存数据
                t1 = threading.Thread(target=save_data, args=(temp, json_name))
                t1.start()
    # 每一个小时要重启一下程序
    # strtime = time.strftime('%Y:%m:%d:%H:%M:%S', time.localtime())
    # if time_temp != str(strtime).split(":")[3]:
    #     print("新的一小时到来！")
    #     os.system("python my_strgy.py")



