#coding=utf-8
import multiprocessing
from multiprocessing import Queue, Process
import json
import websocket
import time
import threading
from send_email import save_data,send_email
import random
import os,signal
# xt开单
from xt_create_order_rest import open_order, close_all,get_xt_account
# GATE开单
from requirement_GN import *

json_name = "gate_xt_BTC日志.json"

try:
    with open('set.json', encoding="utf-8") as file_obj:
        data_temp = json.load(file_obj)
    file_obj.close()
except Exception as e:
    print(e)
class A_wss(object):

    def __init__(self, queue):
        self.queue = queue
        self.url = 'wss://fx-ws.gateio.ws/v4/ws/usdt'

    def on_open(self, ws):
        sub = '{"time" : 123456, "channel" : "futures.order_book", "event": "subscribe", "payload" : ["BTC_USDT", "20", "0"]}'
        ws.send(sub)
        pass

    def on_message(self, ws, message):
        rsl = json.loads(message)
        # print(rsl)
        try:
            # print('ask', rsl['result']['asks'][0]['p'], 'bids', rsl['result']['bids'][0]['p'])
            self.queue.put([[float(rsl['result']['asks'][0]['p']), float(rsl['result']['bids'][0]['p'])],0])
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
            ws.run_forever(ping_interval=30)
        except:
            ws.close()
        return ws


class B_wss(object):

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
        self.A_price = 0
        self.A_buy = 0
        self.A_sell = 0
        self.B_price = 0
        self.B_buy = 0
        self.B_sell = 0
        self.flag = 0
        # 利润
        self.lirun = data_temp['lirun']
        # gate开仓数量
        self.A_volume = data_temp['A_volume']
        # xtde 开仓数量
        self.B_volume = data_temp['B_volume']
        # 条件
        self.tiaojian1 = 0
        self.tiaojian2 = 0


    def domian(self):
        time_end = 0

        # 判断是否拔网线功能
        count_data_A= []
        count_data_B = []
        B_last_price = 0
        A_last_price = 0

        # 开启biybit数据接收
        A_data = A_wss(self.queue)
        one = Process(target=A_data.connection_open_api)
        one.start()
        # 开启xt数据接收
        B_data = B_wss(self.queue)
        two = Process(target=B_data.connection_open_api)
        two.start()

        pid = os.getpid()
        print(pid)
        # 风控
        fengkong = Process(target=self.fengkong,args=(pid,))
        fengkong.start()

        # 平均值
        A_B_buy_list = []
        A_B_sell_list = []
        LEN = 2000
        while 1:
            # 随机数量
            # self.A_volume = round(random.uniform(0.03, 0.05), 2)
            # self.B_volume = int(self.A_volume * 10000)
            print('A', self.A_volume, 'B', self.B_volume, "lirun", self.lirun)
            # print(data_temp)
            data = self.queue.get()
            if data[1] == 0:
                self.A_price = (data[0][0] + data[0][1])/2
                self.A_sell = data[0][0]
                self.A_buy = data[0][1]
            else:
                self.B_price = (data[0][0] + data[0][1])/2
                # 卖一
                self.B_sell = data[0][0]
                self.B_buy = data[0][1]
            if len(A_B_buy_list) > LEN and len(A_B_sell_list) > LEN:
                del A_B_buy_list[0]
                del A_B_sell_list[0]
            if self.A_price != 0 and self.B_price != 0:
                A_B_buy_list.append(self.A_buy-self.B_buy)
                A_B_sell_list.append(self.A_sell-self.B_sell)
                A_B_buy_list_avg_price = sum(A_B_buy_list) / len(A_B_buy_list)
                A_B_sell_list_avg_price = sum(A_B_sell_list) / len(A_B_sell_list)
                print('A-B买一的平均值',sum(A_B_buy_list)/len(A_B_buy_list), 'A-B卖一的平均值', sum(A_B_sell_list)/len(A_B_sell_list), len(A_B_buy_list), len(A_B_sell_list))
            if self.A_price != 0 and self.B_price != 0 and len(A_B_buy_list) > LEN:
                print('A买一', self.A_buy, 'A卖一' ,self.A_sell, 'B买一', self.B_buy, 'A-B买一-平均值', (self.A_buy-self.B_buy)-A_B_buy_list_avg_price, 'A-B卖一-平均值', (self.A_sell-self.B_sell)-A_B_sell_list_avg_price)
            else:
                continue
            # 开仓
            if self.flag == 0:
                # 间隔10秒
                if time.time() - time_end > 10:
                    # A开空  B开多  条件1
                    if (self.A_sell-self.B_sell) - A_B_sell_list_avg_price > self.lirun:
                        time_start = time.time()
                        self.tiaojian1 = 1
                        self.flag = 1
                        # A开空
                        t0 = threading.Thread(target=orders, args=(-self.A_volume, 0, 'BTC_USDT'))
                        t0.start()
                        # B开多
                        t2 = threading.Thread(target=open_order, args=('btc_usdt',self.B_volume,'BUY','LONG',0))
                        t2.start()
                        temp = {}
                        temp['A'] = '开空'
                        temp['B'] = '开多'
                        temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        temp['A卖一'] = self.A_sell
                        temp['B卖一'] = self.B_sell
                        temp['A卖一-B卖一-平均值'] = (self.A_sell-self.B_sell) - A_B_sell_list_avg_price
                        t1 = threading.Thread(target=save_data, args=(temp, json_name))
                        t1.start()
                        pass
                    # A开多  B开空   条件2
                    elif (self.A_buy-self.B_buy) - A_B_buy_list_avg_price < -self.lirun and self.tiaojian1 == 0:
                        time_start = time.time()
                        self.tiaojian2 = 1
                        self.flag = 1
                        # A开多
                        t0 = threading.Thread(target=orders, args=(self.A_volume, 0, 'BTC_USDT'))
                        t0.start()
                        # B开空
                        t2 = threading.Thread(target=open_order, args=('btc_usdt', self.B_volume, 'SELL', 'SHORT', 0))
                        t2.start()
                        temp = {}
                        temp['A'] = '开多'
                        temp['B'] = '开空'
                        temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        temp['A买一'] = self.A_buy
                        temp['B买一'] = self.B_buy
                        temp['A买一-B买一-平均值'] = (self.A_buy-self.B_buy) - A_B_buy_list_avg_price
                        t1 = threading.Thread(target=save_data, args=(temp, json_name))
                        t1.start()
                        pass
            # 平仓
            else:
                # 条件1平仓  A平空  B平多
                if self.tiaojian1 == 1:
                    if (self.A_buy-self.B_buy) - A_B_buy_list_avg_price < -self.lirun + 5 and time.time() - time_start > 180:
                        time_end = time.time()
                        self.tiaojian1 = 0
                        self.flag = 0
                        # A平空
                        t0 = threading.Thread(target=orders, args=(self.A_volume, 0, 'BTC_USDT'))
                        t0.start()
                        # B平多
                        t2 = threading.Thread(target=close_all)
                        t2.start()
                        temp = {}
                        temp['A'] = '平空'
                        temp['B'] = '平多'
                        temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        temp['A买一'] = self.A_buy
                        temp['B买一'] = self.B_buy
                        temp['A买一-B买一-平均值'] = (self.A_buy - self.B_buy) - A_B_buy_list_avg_price
                        t1 = threading.Thread(target=save_data, args=(temp, json_name))
                        t1.start()
                # 条件2平仓 A平多  B平空
                if self.tiaojian2 == 1:
                    if (self.A_sell-self.B_sell) - A_B_sell_list_avg_price > self.lirun - 5 and time.time() - time_start > 180:
                        time_end = time.time()
                        self.tiaojian2 = 0
                        self.flag = 0
                        # A平多
                        t0 = threading.Thread(target=orders, args=(-self.A_volume, 0, 'BTC_USDT'))
                        t0.start()
                        # B平空
                        t2 = threading.Thread(target=close_all)
                        t2.start()
                        temp = {}
                        temp['A'] = '平多'
                        temp['B'] = '平空'
                        temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        temp['A卖一'] = self.A_sell
                        temp['B卖一'] = self.B_sell
                        temp['A卖一-B卖一-平均值'] = (self.A_sell - self.B_sell) - A_B_sell_list_avg_price
                        t1 = threading.Thread(target=save_data, args=(temp, json_name))
                        t1.start()

            # 判断两个交易所是否拔网线
            # A交易所
            if len(count_data_A) == 2000:
                print("A重启", len(count_data_A))
                one.terminate()
                A_data = A_wss(self.queue)
                one = Process(target=A_data.connection_open_api)
                one.start()
                count_data_A = []

            elif A_last_price == self.A_price:
                count_data_A.append(self.A_price)

            else:
                A_last_price = self.A_price
                count_data_A = []

            # B交易所
            if len(count_data_B) == 2000:
                print("B重启", len(count_data_B))
                two.terminate()
                B_data = B_wss(self.queue)
                two = Process(target=B_data.connection_open_api)
                two.start()
                count_data_B = []

            elif B_last_price == self.B_price:
                count_data_B.append(self.B_price)

            else:
                B_last_price = self.B_price
                count_data_B = []



    def fengkong(self,pids):

        while 1:
            time.sleep(10)
            # 查询gate的账户余额
            try:
                if get_gate_acount() < 10:
                    print("资金不足")
                    # xt 一键平仓
                    close_all()
                    # gate
                    size = get_gate_hold()
                    print('gate', size)
                    orders(-size, 0, 'BTC_USDT')
                    send_email('本223', '资金不足')
                    os.kill(pids, signal.SIGINT)

                elif get_xt_account() < 10:
                    print("资金不足")
                    close_all()
                    size = get_gate_hold()
                    print('gate', size)
                    orders(-size, 0, 'BTC_USDT')
                    send_email('本223', '资金不足')
                    os.kill(pids, signal.SIGINT)
                else:
                    print("资金正常")
            except:
                pass





if __name__ == '__main__':
    multiprocessing.freeze_support()
    queue = Queue()
    work = Work(queue)
    three = Process(target=work.domian)
    three.start()
    three.join()