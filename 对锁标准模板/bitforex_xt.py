#coding=utf-8
import multiprocessing
from multiprocessing import Queue, Process
import json
import websocket
import time
import threading
from send_email import save_data
import random
# bitforex开单
from brforex import get_cang
# xt开单
from xt_create_order_rest import open_order, close_all
json_name = "bitforex_xt_BTC日志.json"


class bitforex_wss(object):

    def __init__(self, queue):
        self.queue = queue
        self.url = 'wss://www.bitforex.com/contract/mkapi/ws'
        self.headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'referer': 'https://www.bitforex.com/hk/perpetual/btc_usd',

    }

    def on_open(self, ws):
        data = """[{"type": "subHq", "event": "depth10", "param": {"businessType": "swap-usd-btc", "dType": 0, "size": 100}}]"""
        ws.send(data)

    def on_message(self, ws, message):
        data0 = json.loads(message)
        # print(data0)
        # 处理收到的数据
        data = {}
        if 'asks' in data0['data']:
            # print('ask', data0['data']['asks'][0]['price'], 'bid', data0['data']['bids'][0]['price'])
            self.queue.put([[float(data0['data']['asks'][0]['price']), float(data0['data']['bids'][0]['price'])], 0])


    def on_close(self, ws):
        print("WebSocket连接已关闭，将在1秒后重新连接...")
        time.sleep(1)
        self.connection_open_api()

    def on_error(self, ws, error):
        print('出现错误')
        print(error)
        self.connection_open_api()

    def connection_open_api(self):
        try:
            ws = websocket.WebSocketApp(self.url,
                                        header=self.headers,
                                        on_open=self.on_open,
                                        on_message=self.on_message,
                                        on_close=self.on_close,
                                        on_error=self.on_error)
            ws.run_forever()
        except:
            print("连接异常，将在1秒后重新连接...")
            time.sleep(1)


class Xt_wss(object):

    def __init__(self, queue):
        self.queue = queue
        self.url = 'wss://fstream.xt.com/ws/market?type=SYMBOL'   # 现货  将f去掉
        self.Symbollist = ['BTC']
        self.Steamlist = []
        self.allA =[]
        self.allB = []
        self.aPrice = 0
        self.bPrice = 0
        self.allSetA = set()
        self.allSetB = set()

    def on_open(self, ws):
        msg = '{"method":"subscribe","params":["ticker@btc_usdt","trade@btc_usdt","depth_update@btc_usdt","index_price@btc_usdt","mark_price@btc_usdt","fund_rate@btc_usdt"]}'
        ws.send(msg)

    def on_message(self, ws, message):
        if int(time.time()) % 10 == 0:
            ws.send('ping')
        try:
            rsl = json.loads(message)

            if rsl["topic"] == "depth_update":

                aparam = rsl["data"]["a"]
                bparam = rsl["data"]["b"]
                for a in aparam:
                    #print(a)
                    if float(a[0]) in self.allA:
                        if a[1] == '0':
                            del self.allA[self.allA.index(float(a[0]))]
                    else:
                        if a[1] != '0':
                            self.allA.append(float(a[0]))
                for b in bparam:
                    if float(b[0]) in self.allB:
                        if b[1] == '0':
                            del self.allB[self.allB.index(float(b[0]))]
                    else:
                        if b[1] != '0':
                            self.allB.append(float(b[0]))
                bparam = rsl["data"]["b"]
                self.aPrice,self.bPrice = sorted(self.allA)[0],sorted(self.allB)[-1]
                # print('卖一', self.aPrice, '买一', self.bPrice)
                self.queue.put([[float(self.aPrice), float(self.bPrice)], 1])
                #print(len(self.allB))
        except :
            pass

    def on_error(self, ws, error):

        print(str(error))

    def on_close(self, ws, param='', param2=''):
        print(" Open Connection closed")
        self.connection_open_api()

    def connection_open_api(self):
        # websocket.enableTrace(True)
        # 调试日志是否开启
        ws = websocket.WebSocketApp(self.url,
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

    def __init__(self, queue):
        self.queue = queue
        self.bkex_price = 0
        self.bkex_buy = 0
        self.bkex_sell = 0
        self.xt_price = 0
        self.xt_buy = 0
        self.xt_sell = 0
        self.flag = 0
        # 利润
        self.lirun = 20
        # bkex开仓数量
        self.bkex_volume = 400
        # xtde 开仓数量
        self.xt_volume = 140

    def domian(self):
        tiaojian1 = 0
        tiaojian2 = 0
        time_end = 0

        # 判断是否拔网线功能
        count_data_bkex = []
        count_data_xt = []
        xt_last_price = 0
        bkex_last_price = 0

        # 开启biybit数据接收
        bkex_wss = bitforex_wss(self.queue)
        one = Process(target=bkex_wss.connection_open_api)
        one.start()
        # 开启xt数据接收
        work1 = Xt_wss(self.queue)
        two = Process(target=work1.connection_open_api)
        two.start()

        # 平均值
        bkex_xt_buy_list = []
        bkex_xt_sell_list = []
        LEN = 2000
        while 1:
            # 随机数量
            # self.bkex_volume = round(random.uniform(0.05, 0.12), 2)
            # self.xt_volume = int(self.bkex_volume * 10000)
            print('bkex', self.bkex_volume, 'xt', self.xt_volume)

            data = self.queue.get()
            print(data)
            # print(data)
            if data[1] == 0:
                self.bkex_price = (data[0][0] + data[0][1])/2
                self.bkex_sell = data[0][0]
                self.bkex_buy = data[0][1]
            else:
                self.xt_price = (data[0][0] + data[0][1])/2
                # 卖一
                self.xt_sell = data[0][0]
                self.xt_buy = data[0][1]
            if len(bkex_xt_buy_list) > LEN and len(bkex_xt_sell_list) > LEN:
                del bkex_xt_buy_list[0]
                del bkex_xt_sell_list[0]
            if self.xt_price != 0 and self.bkex_price != 0:
                bkex_xt_buy_list.append(self.xt_buy-self.bkex_buy)
                bkex_xt_sell_list.append(self.xt_sell-self.bkex_buy)
                bkex_xt_buy_list_avg_price = sum(bkex_xt_buy_list) / len(bkex_xt_buy_list)
                bkex_xt_sell_list_avg_price = sum(bkex_xt_sell_list) / len(bkex_xt_sell_list)
                print('xt-bitforex买一的平均值',sum(bkex_xt_buy_list)/len(bkex_xt_buy_list), 'xt-bitforex卖一的平均值', sum(bkex_xt_sell_list)/len(bkex_xt_sell_list), len(bkex_xt_buy_list), len(bkex_xt_sell_list))
            if self.xt_price != 0 and self.bkex_price != 0 and len(bkex_xt_buy_list) > LEN:
                print('xt买一', self.xt_buy, 'xt卖一' ,self.xt_sell, 'bitforex的最新价格', self.bkex_price, 'xt-bitforex买一-平均值', (self.xt_buy-self.bkex_price)-bkex_xt_buy_list_avg_price, 'xt-bitforex卖一-平均值', (self.xt_sell-self.bkex_price)-bkex_xt_sell_list_avg_price)
            else:
                continue
            # 开仓
            if self.flag == 0 and time.time() - time_end > 10:
                # bitforex开多  xt开空  条件1
                if (self.xt_sell-self.bkex_sell) - bkex_xt_sell_list_avg_price > self.lirun:
                    time_start = time.time()
                    tiaojian1 = 1
                    self.flag = 1
                    # xt开空
                    t0 = threading.Thread(target=open_order, args=('btc_usdt', self.xt_volume, 'SELL', 'SHORT', 0))
                    t0.start()
                    # bitforex开多
                    t1 = threading.Thread(target=get_cang, args=(1, self.bkex_volume, self.bkex_sell+5, 1))
                    t1.start()
                    temp = {}
                    temp['bkex'] = '开多'
                    temp['xt'] = '开空'
                    temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    temp['xt卖一'] = self.xt_sell
                    temp['bkex卖一'] = self.bkex_sell
                    temp['xt卖一-bkex卖一-平均值'] = (self.xt_sell-self.bkex_sell) - bkex_xt_sell_list_avg_price
                    t1 = threading.Thread(target=save_data, args=(temp, json_name))
                    t1.start()
                    pass
                # xt开多  bitforex开空   条件2
                elif (self.xt_buy-self.bkex_buy) - bkex_xt_buy_list_avg_price < -self.lirun and self.flag == 0:
                    time_start = time.time()
                    tiaojian2 = 1
                    self.flag = 1
                    # xt开多
                    t0 = threading.Thread(target=open_order, args=('btc_usdt',self.xt_volume,'BUY','LONG',0))
                    t0.start()
                    # bitforex开空
                    t1 = threading.Thread(target=get_cang, args=(2, self.bkex_volume, self.bkex_buy-5, 1))
                    t1.start()
                    temp = {}
                    temp['bkex'] = '开空'
                    temp['xt'] = '开多'
                    temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    temp['xt买一'] = self.xt_buy
                    temp['bkex买一'] = self.bkex_buy
                    temp['xt买一-bkex买一-平均值'] = (self.xt_buy-self.bkex_buy) - bkex_xt_buy_list_avg_price
                    t1 = threading.Thread(target=save_data, args=(temp, json_name))
                    t1.start()
                    pass
            # 平仓
            else:
                # 条件1平仓  xt平空  bitforex平多
                if tiaojian1 == 1 and (self.xt_buy-self.bkex_buy) - bkex_xt_buy_list_avg_price < -self.lirun and time.time() - time_start > 180:
                    time_end = time.time()
                    tiaojian1 = 0
                    self.flag = 0
                    # bitforex平多
                    t0 = threading.Thread(target=get_cang, args=(2, self.bkex_volume, 0, 2))
                    t0.start()
                    # xt平空
                    t2 = threading.Thread(target=close_all)
                    t2.start()
                    temp = {}
                    temp['bkex'] = '平多'
                    temp['xt'] = '平空'
                    temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    temp['xt买一'] = self.xt_buy
                    temp['bkex买一'] = self.bkex_buy
                    temp['xt买一-bkex买一-平均值'] = (self.xt_buy-self.bkex_buy) - bkex_xt_buy_list_avg_price
                    t1 = threading.Thread(target=save_data, args=(temp, json_name))
                    t1.start()
                # 条件2平仓 xt平多  bitforex平空
                if tiaojian2 == 1 and (self.xt_sell-self.bkex_sell) - bkex_xt_sell_list_avg_price > self.lirun and time.time() - time_start > 180:
                    time_end = time.time()
                    tiaojian2 = 0
                    self.flag = 0
                    # bitforex平空
                    t0 = threading.Thread(target=get_cang,args=(1, self.bkex_volume, 0, 2))
                    t0.start()
                    # xt平多
                    t2 = threading.Thread(target=close_all)
                    t2.start()
                    temp = {}
                    temp['bkex'] = '平空'
                    temp['xt'] = '平多'
                    temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    temp['xt卖一'] = self.xt_sell
                    temp['bkex卖一'] = self.bkex_sell
                    temp['bkex卖一-xt卖一-平均值'] = (self.xt_sell-self.bkex_sell) - bkex_xt_sell_list_avg_price
                    t1 = threading.Thread(target=save_data, args=(temp, json_name))
                    t1.start()

            # 判断两个交易所是否拔网线
            # bybit交易所
            if len(count_data_bkex) == 2000:
                print("重启", len(count_data_bkex))
                one.terminate()
                bkex_wss = bitforex_wss(self.queue)
                one = Process(target=bkex_wss.connection_open_api)
                one.start()

            elif bkex_last_price == self.bkex_price:
                count_data_bkex.append(self.bkex_price)

            else:
                bkex_last_price = self.bkex_price
                count_data_bkex = []

            # xt交易所
            if len(count_data_xt) == 2000:
                print("重启", len(count_data_xt))
                two.terminate()
                work1 = Xt_wss(self.queue)
                two = Process(target=work1.connection_open_api)
                two.start()

            elif xt_last_price == self.xt_price:
                count_data_bkex.append(self.xt_price)

            else:
                xt_last_price = self.xt_price
                count_data_xt = []
        pass

if __name__ == '__main__':
    multiprocessing.freeze_support()
    queue = Queue()
    # work0 = Work(queue)
    # work1 = Work1(queue)
    work = Work(queue)
    # one = Process(target=work0.connection_open_api)
    # two = Process(target=work1.connection_open_api)
    three = Process(target=work.domian)
    # one.start()
    # two.start()
    three.start()
    # one.join()
    # two.join()
    three.join()