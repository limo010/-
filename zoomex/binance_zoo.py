import websocket
import json
import random
from multiprocessing import Manager, Process, Queue
import multiprocessing
import os
import time
import threading
from send_email import save_data
import ssl
from zoo_create_order import create_order

json_name = '日志.json'

class Binance_wss(object):

    def __init__(self, queue):
        self.queue = queue
        url = 'wss://fstream.binance.com'   # 现货  将f去掉
        self.Symbollist = ['BTC']
        self.Steamlist = []
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
        # print(data)
        # price_buy = data['a'][0][0]  # eth asks
        # price_sell = data['b'][0][0]  # eth bids
        price_zuixin = data['p']
        temp = {}
        for symbol in self.Symbollist:
            if symbol.lower() in stream or symbol.upper() in stream:
                # print('%s买一价：%s，卖一价：%s' % (symbol, str(price_buy), str(price_sell)))
                # print("最新价:"+str(price_zuixin))
                # temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                # self.progress_list[0] = [float(price_buy), float(price_sell)]
                self.queue.put([[float(price_zuixin),0], 0])
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
            ws.run_forever(ping_interval=30, sslopt={"cert_reqs": ssl.CERT_NONE})
        except:
            ws.close()
        return ws

class Zoo_wss(object):

    def __init__(self, queue):
        self.queue = queue
        self.url = 'wss://stream.zoomex.com/usdt_public'

    def on_open(self, ws):
        ws.send('{"op": "subscribe", "args": ["instrument_info.100ms.BTCUSDT-Perp"]}')
        pass

    def on_message(self, ws, message):
        rsl = json.loads(message)
        try:
            # print(rsl)
            self.queue.put([[float(rsl['data']['update'][0]['last_price']), 0], 1])
        except:
            pass
    def on_error(self, ws, error):
        print(str(error))

    def on_close(self, ws, param='', param2=''):
        self.connection_open_api()

    def connection_open_api(self):
        # 调试日志是否开启
        ws = websocket.WebSocketApp(self.url,
                                    on_open=self.on_open,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        try:
            ws.run_forever(ping_interval=30,sslopt={"cert_reqs": ssl.CERT_NONE})
        except:
            ws.close()
        return ws

class Work(object):

    def __init__(self, queue,List):
        self.queue = queue
        self.binance_price = 0
        self.binance_sell = 0
        self.binance_buy = 0
        self.zoo_price = 0
        self.zoo_sell = 0
        self.zoo_buy = 0
        self.flag = 0
        self.profit = 15
        # self.hc_volume = data_temp['hc_volume']
        # self.xt_volume = data_temp['xt_volume']
        self.List = List

    def domian(self):
        apiKey = "rD7nfjacvdRB9ogWuw"
        secret = "FwsujmWdGEet7S4ZC3FB5yIp7hqIrTGvxLco"
        tiaojian1 = 0
        tiaojian1_1 = 0
        tiaojian2 = 0
        tiaojian2_1 = 0
        time_end = 0
        chicang = 0
        work1 = Binance_wss(self.queue)
        one = Process(target=work1.connection_open_api)

        work2 = Zoo_wss(self.queue)
        two = Process(target=work2.connection_open_api)

        one.start()
        two.start()

        pid = os.getpid()
        print(pid)
        # 风控1 统计本金是否充足
        # fengkong = Process(target=self.fengkong, args=(pid,))
        # fengkong.start()
        # 风控2 平仓信号处理
        # fengkong2 = Process(target=self.close_check)
        # fengkong2.start()

        # bn_zoo_buy_list = []
        # bn_zoo_sell_list = []
        bn_zoo_list = []
        LEN = 2000

        while True:
            data = self.queue.get()
            # 平仓信号发送
            self.List[0] = chicang
            # print(data)
            # bn的数据
            if data[1] == 0:
                self.binance_price = data[0][0]
            # zoo的数据
            else:
                self.zoo_price = data[0][0]

            if len(bn_zoo_list) > LEN and len(bn_zoo_list) > LEN:
                del bn_zoo_list[0]
                del bn_zoo_list[0]

            if self.zoo_price != 0 and self.binance_price != 0:
                bn_zoo_list.append(self.binance_price - self.zoo_price)
                bn_zoo_list_avg_price = sum(bn_zoo_list) / len(bn_zoo_list)
                print('bn最新价-zoo最新价的平均值', bn_zoo_list_avg_price, len(bn_zoo_list))
            if self.zoo_price != 0 and self.binance_price != 0 and len(bn_zoo_list) > LEN:
                print('bn最新价', self.binance_price, 'zoo最新价', self.zoo_price,  'bn最新价-zoo最新价-平均值',(self.binance_price - self.zoo_price) - bn_zoo_list_avg_price)
            else:
                continue
            # xt开多
            if self.flag == 0 and tiaojian1 == 0:
                if time.time()-time_end > 10:
                    # xt开多  条件1
                    if (self.binance_price - self.zoo_price) - bn_zoo_list_avg_price > self.profit and abs(self.binance_price-self.zoo_price) < 100:
                        tiaojian1 = 1
                        self.flag = 1
                        chicang = 1
                        # xt开多
                        t2 = threading.Thread(target=create_order, args=(apiKey, secret, 'BTCUSDT-Perp', 'Buy', 'Market', '0.001', '0', '1'))
                        t2.start()
                        temp = {}
                        temp['zoo'] = '开多'
                        temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        temp['zoo最新价'] = self.zoo_price
                        temp['bn最新价 - zoo最新价-平均值'] = (self.binance_price - self.zoo_price) - bn_zoo_list_avg_price
                        t1 = threading.Thread(target=save_data, args=(temp, json_name))
                        t1.start()
                        pass
            # xt开多之后开空
            if self.flag == 1 and tiaojian1 == 1 and tiaojian1_1 == 0:
                # xt开空
                if (self.binance_price - self.zoo_price) - bn_zoo_list_avg_price < 5 and abs(self.binance_price-self.zoo_price) < 100:
                    time_start = time.time()
                    tiaojian1_1 = 1
                    chicang = 1
                    # xt开空
                    t2 = threading.Thread(target=create_order, args=(apiKey, secret, 'BTCUSDT-Perp', 'Sell', 'Market', '0.001', '0', '2'))
                    t2.start()
                    temp = {}
                    temp['zoo'] = '开空'
                    temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    temp['zoo最新价'] = self.zoo_price
                    temp['bn最新价 - zoo最新价-平均值'] = (self.binance_price - self.zoo_price) - bn_zoo_list_avg_price
                    t1 = threading.Thread(target=save_data, args=(temp, json_name))
                    t1.start()
                    pass
            # xt开空
            if self.flag == 0 and tiaojian2 == 0:
                if time.time() - time_end > 10:
                    # xt开空
                    if (self.binance_price - self.zoo_price) - bn_zoo_list_avg_price < - self.profit and abs(self.binance_price - self.zoo_price) < 100:
                        tiaojian2 = 1
                        self.flag = 1
                        chicang = 1
                        # xt开空
                        t2 = threading.Thread(target=create_order, args=(apiKey, secret, 'BTCUSDT-Perp', 'Sell', 'Market', '0.001', '0', '2'))
                        t2.start()
                        temp = {}
                        temp['zoo'] = '开空'
                        temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        temp['zoo最新价'] = self.zoo_price
                        temp['bn最新价 - zoo最新价-平均值'] = (self.binance_price - self.zoo_price) - bn_zoo_list_avg_price
                        t1 = threading.Thread(target=save_data, args=(temp, json_name))
                        t1.start()
                        pass
            # xt开空之后开多
            if self.flag == 1 and tiaojian2 == 1 and tiaojian2_1 == 0:
                if (self.binance_price - self.zoo_price) - bn_zoo_list_avg_price > - 5 and abs(self.binance_price - self.zoo_price) < 100:
                    tiaojian2_1 = 1
                    chicang = 1
                    time_start = time.time()
                    # xt开多
                    t2 = threading.Thread(target=create_order, args=(apiKey, secret, 'BTCUSDT-Perp', 'Buy', 'Market', '0.001', '0', '1'))
                    t2.start()
                    temp = {}
                    temp['zoo'] = '开多'
                    temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    temp['zoo最新价'] = self.zoo_price
                    temp['bn最新价 - zoo最新价-平均值'] = (self.binance_price - self.zoo_price) - bn_zoo_list_avg_price
                    t1 = threading.Thread(target=save_data, args=(temp, json_name))
                    t1.start()
                    pass

            # 平仓 平多
            if self.flag == 1 and tiaojian1_1 == 1:
                if time.time() - time_start > 60:
                    if tiaojian1 == 1:
                        # 持仓不能大于10分钟
                        if (self.binance_price - self.zoo_price) - bn_zoo_list_avg_price < - self.profit and abs(self.binance_price - self.zoo_price) < 100:
                            tiaojian1 = 0
                            # xt平多
                            t2 = threading.Thread(target=create_order, args=(apiKey, secret, 'BTCUSDT-Perp', 'Sell', 'Market', '0.001', '0', '1'))
                            t2.start()
                            temp = {}
                            temp['zoo'] = '平多'
                            temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                            temp['zoo最新价'] = self.zoo_price
                            temp['bn最新价-zoo最新价-平均值'] = (self.binance_price - self.zoo_price) - bn_zoo_list_avg_price
                            t1 = threading.Thread(target=save_data, args=(temp, json_name))
                            t1.start()
            # 平多了之后平空
            if self.flag == 1 and tiaojian1_1 == 1 and tiaojian1 == 0:
                if (self.binance_price - self.zoo_price) - bn_zoo_list_avg_price > - 5 and abs(self.binance_price - self.zoo_price) < 100:
                    time_end = time.time()
                    tiaojian1_1 = 0
                    self.flag = 0
                    chicang = 0
                    # xt平空
                    t2 = threading.Thread(target=create_order, args=(apiKey, secret, 'BTCUSDT-Perp', 'Buy', 'Market', '0.001', '0', '2'))
                    t2.start()
                    temp = {}
                    temp['zoo'] = '平空'
                    temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    temp['zoo最新价'] = self.zoo_price
                    temp['bn最新价-zoo最新价-平均值'] = (self.binance_price - self.zoo_price) - bn_zoo_list_avg_price
                    t1 = threading.Thread(target=save_data, args=(temp, json_name))
                    t1.start()
            # 平空
            if self.flag == 1 and tiaojian2_1 == 1:
                if time.time() - time_start > 60:
                    if tiaojian2 == 1:
                        if (self.binance_price - self.zoo_price) - bn_zoo_list_avg_price > self.profit and abs(self.binance_price - self.zoo_price) < 100:
                            tiaojian2 = 0
                            # xt平空
                            t2 = threading.Thread(target=create_order, args=(apiKey, secret, 'BTCUSDT-Perp', 'Buy', 'Market', '0.001', '0', '2'))
                            t2.start()
                            temp = {}
                            temp['zoo'] = '平空'
                            temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                            temp['zoo最新价'] = self.zoo_price
                            temp['bn最新价-xt最新价-平均值'] = (self.binance_price - self.zoo_price) - bn_zoo_list_avg_price
                            t1 = threading.Thread(target=save_data, args=(temp, json_name))
                            t1.start()
            # 平空了之后平多
            if self.flag == 1 and tiaojian2_1 == 1 and tiaojian2 == 0:
                if (self.binance_price - self.zoo_price) - bn_zoo_list_avg_price < 5 and abs(self.binance_price - self.zoo_price) < 100:
                    time_end = time.time()
                    tiaojian2_1 = 0
                    self.flag = 0
                    chicang = 0
                    # xt平多
                    t2 = threading.Thread(target=create_order, args=(apiKey, secret, 'BTCUSDT-Perp', 'Sell', 'Market', '0.001', '0', '1'))
                    t2.start()
                    temp = {}
                    temp['zoo'] = '平多'
                    temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    temp['zoo最新价'] = self.zoo_price
                    temp['bn最新价-zoo最新价-平均值'] = (self.binance_price - self.zoo_price) - bn_zoo_list_avg_price
                    t1 = threading.Thread(target=save_data, args=(temp, json_name))
                    t1.start()
        pass

if __name__ == '__main__':
    multiprocessing.freeze_support()
    queue = Queue()
    List = Manager().list()
    List.append(0)
    work = Work(queue, List)
    three = Process(target=work.domian)
    three.start()
    three.join()