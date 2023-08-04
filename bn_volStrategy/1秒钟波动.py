import requests
import json
import numpy as np
import time
from json_create import save_data
import threading
import random
import websocket
import ssl
import multiprocessing
from multiprocessing import Manager, Process, Queue

json_name = "1秒钟波动日志.json"

# 拿币安现货的数据
class Bn_data_wss(object):

    def __init__(self, queue, List, symbol):
        self.queue = queue
        self.List = List
        url = 'wss://fstream.binance.com'   # 现货  将f去掉
        self.Symbollist = [symbol]
        self.Steamlist = []
        self.data_list = []
        for symbol in self.Symbollist:
            self.Steamlist.append(symbol.lower() + 'usdt@aggTrade')   # @aggTrade (最新成交价)  depth5@100ms（深度）
        if len(self.Steamlist) == 1:
            self.open_url = url + '/ws/' + self.Steamlist[0]
        else:
            parameters = '/stream?streams='
            for v in self.Steamlist:
                parameters += f"{v}/"
            parameters = parameters[:-1]
            self.open_url = url + parameters

    def on_open(self, ws):
        pass

    def on_message(self, ws, message):
        if message == 'ping':
            ws.send('pong')
        rsl = json.loads(message)
        # print(rsl)
        if len(self.data_list) > 20:
            del self.data_list[0]
        if len(self.Steamlist) == 1:
            stream = self.Symbollist
            data = rsl
        else:
            if 'data' in rsl:
                stream = rsl['stream']
                data = rsl['data']
            else:
                print('非正常数据')
                return ws
        L1 = random.randint(1, 7500)
        if L1 == 100:
            print('币安合约价格推送正常运行中')
        price_zuixin = data['p']
        self.data_list.append(float(price_zuixin))
        self.List[1] = sum(self.data_list) / len(self.data_list)
        for symbol in self.Symbollist:
            if symbol.lower() in stream or symbol.upper() in stream:
                self.queue.put([[float(price_zuixin),0], 0])
                self.List[0] = float(price_zuixin)
                # print("最新价:", str(price_zuixin), '近20个价格的平均值', self.List[1])
                break

    def on_error(self, ws, error):

        print(str(error))

    def on_close(self, ws, param='', param2=''):
        print("Binance Open Connection closed")
        self.connection_open_api()

    def connection_open_api(self):
        # websocket.enableTrace(True)
        # 调试日志是否开启
        ws = websocket.WebSocketApp(self.open_url,
                                    on_open=self.on_open,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        try:
            ws.run_forever(ping_interval=30)
        except:
            ws.close()
        return ws

class Work(object):

    def __init__(self,queue, List):
        self.queue = queue
        self.List = List
        pass

    # 输入毫秒级的时间，转出正常格式的时间
    def timeStamp(self, timeNum):
        timeStamp = float(timeNum/1000)
        timeArray = time.localtime(timeStamp)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        # print (otherStyleTime)
        return otherStyleTime


    def domain(self):
        ms500 = 0
        ms1000 = 0
        flag = 0
        open_time = ""
        duocang = 0
        kongcang = 0
        # 一秒钟波动变量
        shangyici_price = 0  # 代表上一次的价格
        while 1:
            # 开仓前
            if flag == 0:
                # 市价开多
                time_temp = time.time()
                if time_temp - ms500 > 0.5 or time_temp - ms1000 > 1:
                    if time_temp - ms500 > 0.5:
                        ms500 = time_temp
                    if time_temp - ms1000 > 1:
                        ms1000 = time_temp

                    if self.List[0] - shangyici_price > 20 and shangyici_price != 0:
                        flag = 1
                        duocang = 1

                        temp = {}
                        temp['open'] = '开多'
                        temp['开盘时间'] = self.List[2]
                        temp['开仓时间'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        temp['上->1ms/0.5ms价格'] = shangyici_price
                        temp['开多价'] = self.List[0]
                        temp['guadan'] = "挂空单"


                        open_time = self.List[2]
                        # 挂空单
                        open_price = self.List[0]
                        # 挂单价上下少两个价格


                        # 保存数据
                        t1 = threading.Thread(target=save_data, args=(temp, json_name))
                        t1.start()
                    # 市价开空
                    elif self.List[0] - shangyici_price < -20 and shangyici_price != 0 and flag == 0:
                        flag = 1
                        kongcang = 1
                        temp = {}
                        temp['open'] = '开空'
                        temp['开盘时间'] = self.List[2]
                        temp['开仓时间'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        temp['上->1ms/0.5ms价格'] = shangyici_price
                        temp['开空价'] = self.List[0]
                        temp['guadan'] = "挂多单"

                        open_time = self.List[2]
                        # 挂多单
                        open_price = self.List[0]
                        # 挂单价上下少两个价格

                        # 保存数据
                        t1 = threading.Thread(target=save_data, args=(temp, json_name))
                        t1.start()

                    shangyici_price = self.List[0]
            # 开仓后
            else:
                # K线收盘平仓
                if self.List[2] != open_time:
                    flag = 0
                    duocang = 0
                    kongcang = 0
                    print('平仓')
                    temp = {}
                    temp['open'] = '平仓'
                    temp['最新价'] = self.List[0]
                    temp['平仓时间'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    # 取消所有挂单


                    # 保存数据
                    t1 = threading.Thread(target=save_data, args=(temp, json_name))
                    t1.start()
                if duocang == 1:
                    if self.List[0] - open_price < 0:
                        print("平多仓")
                        # 检测是否开出空单，开出则挂多单，否则取消挂单
                        kongcang = 1
                        duocang = 0
                        temp = {}
                        temp['open'] = "行情反转平多单"
                        temp['guadan'] = "挂多单"
                        temp['最新价'] = self.List[0]
                        temp['平仓/挂单时间'] = time.strftime('%Y-%m-%d %H:%M:%S')


                        # 保存数据
                        t1 = threading.Thread(target=save_data, args=(temp, json_name))
                        t1.start()
                if kongcang == 1:
                    if self.List[0] - open_price > 0:
                        print("平空仓")
                        # 检测是否开出多单，开出则挂空单，否则取消挂单
                        duocang = 1
                        kongcang = 0
                        temp = {}
                        temp['open'] = "行情反转平空单"
                        temp['guadan'] = "挂空单"
                        temp['最新价'] = self.List[0]
                        temp['平仓/挂单时间'] = time.strftime('%Y-%m-%d %H:%M:%S')


                        # 保存数据
                        t1 = threading.Thread(target=save_data, args=(temp, json_name))
                        t1.start()

                shangyici_price = self.List[0]

    def get_open_time(self):
        url = 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=10'
        while 1:
            time.sleep(1)
            try:
                response = requests.get(url)
                data = response.json()
            except:
                continue
            self.List[2] = str(self.timeStamp(data[-1][0]))
            print('开盘时间', self.List[2], '最新价', self.List[0])
        pass



if __name__ == '__main__':
    multiprocessing.freeze_support()
    List = Manager().list()
    List.append(0)
    List.append(1)
    List.append(2)
    queue = Queue()

    work2 = Bn_data_wss(queue, List, "BTC")
    two = Process(target=work2.connection_open_api)

    work = Work(queue,List)
    one = Process(target=work.domain)

    three = Process(target=work.get_open_time)
    one.start()
    two.start()
    three.start()
    one.join()
    two.join()
    three.join()
    pass


