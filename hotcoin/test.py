import websocket
import json
import time
import multiprocessing
import threading
from base_util_xt import open_order, close_all
from json_create import save_data
import query_paks
from multiprocessing import Manager, Process, Queue

json_name = "hc_xt_BTC日志.json"
# hotcoin api-key
ACCESS_KEY = ""
SECRET_KEY = ""

class hotcoin_wss(object):
    def __init__(self, queue):
        self.queue = queue
        self.url = 'wss://wss-ct.hotcoin.fit'
    def on_open(self, ws):
        sub = '{"event": "subscribe","params": {"biz": "perpetual","type": "depth","contractCode": "btcusdt","zip": false,"serialize": false}}'
        ws.send(sub)
        pass
    def on_message(self, ws, message):
        if int(time.time()) % 10 == 0:
            ws.send('ping')
        rsl = json.loads(message)
        try:
            if 'asks' in rsl['data']:
                self.queue.put([[float(rsl['data']['asks'][0][0]), float(rsl['data']['bids'][0][0])], 0])
        except:
            pass
    def on_error(self, ws, error):
        print(str(error))
    def on_close(self, ws, param1='', param2=''):
        self.connection_open_api()
    def connection_open_api(self):
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

class xt_wss(object):
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
                #tparam = rsl['data']['t']
                for a in aparam:
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
                #print('卖一', self.aPrice, '买一', self.bPrice)
                self.queue.put([[float(self.aPrice), float(self.bPrice)], 1])
        except :
            pass

    def on_error(self, ws, error):

        print(str(error))

    def on_close(self, ws, param='', param2=''):
        print(" Open Connection closed")
        self.connection_open_api()

    def connection_open_api(self):
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
        self.hc_price = 0
        self.hc_sell = 0
        self.hc_buy = 0
        self.xt_price = 0
        self.xt_sell = 0
        self.xt_buy = 0
        self.flag = 0
        self.profit = 15

    def domian(self):
        tiaojian1 = 0
        tiaojian2 = 0
        time_end = 0

        work1 = hotcoin_wss(self.queue)
        one = Process(target=work1.connection_open_api)

        work2 = xt_wss(self.queue)
        two = Process(target=work2.connection_open_api)

        one.start()
        two.start()

        hc_xt_buy_list = []
        hc_xt_sell_list = []
        LEN = 2000

        while True:
            data = self.queue.get()
            print(data)
            if data[1] == 0:
                self.hc_price = (data[0][0] + data[0][1]) / 2
                self.hc_sell = data[0][0]
                self.hc_buy = data[0][1]
            else:
                self.xt_price = (data[0][0] + data[0][1]) / 2
                self.xt_sell = data[0][0]
                self.xt_buy = data[0][1]

            if len(hc_xt_buy_list) > LEN and len(hc_xt_sell_list) > LEN:
                del hc_xt_buy_list[0]
                del hc_xt_sell_list[0]

            if self.xt_price != 0 and self.hc_price != 0:
                hc_xt_buy_list.append(self.hc_buy - self.xt_buy)
                hc_xt_sell_list.append(self.hc_sell - self.xt_sell)
                hc_xt_buy_list_avg_price = sum(hc_xt_buy_list) / len(hc_xt_buy_list)
                hc_xt_sell_list_avg_price = sum(hc_xt_sell_list) / len(hc_xt_sell_list)
                print('hc-xt买一的平均值', hc_xt_buy_list_avg_price, 'hc-xt卖一的平均值',hc_xt_sell_list_avg_price, len(hc_xt_buy_list), len(hc_xt_sell_list))
            if self.xt_price != 0 and self.hc_price != 0 and len(hc_xt_buy_list) > LEN:
                print('xt买一', self.xt_buy, 'xt卖一', self.xt_sell, 'hc的最新价格', self.hc_price, 'hc-xt买一-平均值',(self.hc_price - self.xt_buy) - hc_xt_buy_list_avg_price, 'hc-xt卖一-平均值',(self.hc_price - self.xt_sell) - hc_xt_sell_list_avg_price)
            else:
                continue
            # 开仓
            if self.flag == 0:
                if time.time()-time_end > 10:
                    # hc开空  xt开多  条件1
                    if (self.hc_sell - self.xt_sell) - hc_xt_sell_list_avg_price > self.profit:
                        time_start = time.time()
                        tiaojian1 = 1
                        self.flag = 1
                        # hc开空
                        t0 = threading.Thread(target=query_paks.order_processor, args=(ACCESS_KEY, SECRET_KEY, '11', 'open_short', 1))
                        t0.start()
                        # xt开多
                        t2 = threading.Thread(target=open_order, args=('btc_usdt', 100, 'BUY', 'LONG', 0))
                        t2.start()
                        temp = {}
                        temp['hc'] = '开空'
                        temp['xt'] = '开多'
                        temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        temp['xt卖一'] = self.xt_sell
                        temp['hc卖一'] = self.hc_sell
                        temp['hc卖一-xt卖一-平均值'] = (self.hc_sell - self.xt_sell) - hc_xt_sell_list_avg_price
                        t1 = threading.Thread(target=save_data, args=(temp, json_name))
                        t1.start()
                        pass
                    # hc开多  xt开空   条件2
                    elif (self.hc_buy - self.xt_buy) - hc_xt_buy_list_avg_price < -self.profit and self.flag == 0:
                        time_start = time.time()
                        tiaojian2 = 1
                        self.flag = 1
                        # hc开多
                        t0 = threading.Thread(target=query_paks.order_processor, args=(ACCESS_KEY, SECRET_KEY, '11', 'open_long', 1))
                        t0.start()
                        # xt开空
                        t2 = threading.Thread(target=open_order, args=('btc_usdt', 100, 'SELL', 'SHORT', 0))
                        t2.start()
                        temp = {}
                        temp['hc'] = '开多'
                        temp['xt'] = '开空'
                        temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        temp['xt买一'] = self.xt_buy
                        temp['hc买一'] = self.hc_buy
                        temp['hc买一-xt买一-平均值'] = (self.hc_buy - self.xt_buy) - hc_xt_buy_list_avg_price
                        t1 = threading.Thread(target=save_data, args=(temp, json_name))
                        t1.start()
                        pass
            # 平仓
            else:
                # 条件1平仓  hc平空  xt平多
                if time.time() - time_start > 300:
                    if tiaojian1 == 1:
                        if (self.hc_buy - self.xt_buy) - hc_xt_buy_list_avg_price < -self.profit:
                            time_end = time.time()
                            tiaojian1 = 0
                            self.flag = 0
                            # hc平空
                            t0 = threading.Thread(target=query_paks.order_liquidation, args=(ACCESS_KEY, SECRET_KEY, "SHORT"))
                            t0.start()
                            # xt平多
                            t2 = threading.Thread(target=close_all)
                            t2.start()
                            temp = {}
                            temp['hc'] = '平空'
                            temp['xt'] = '平多'
                            temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                            temp['xt买一'] = self.xt_buy
                            temp['hc买一'] = self.hc_buy
                            temp['hc买一-xt买一-平均值'] = (self.hc_buy - self.xt_buy) - hc_xt_buy_list_avg_price
                            t1 = threading.Thread(target=save_data, args=(temp, json_name))
                            t1.start()
                    # 条件2平仓 hc平多  xt平空
                    if tiaojian2 == 1:
                        if (self.hc_sell - self.xt_sell) - hc_xt_sell_list_avg_price > self.profit:
                            time_end = time.time()
                            tiaojian2 = 0
                            self.flag = 0
                            # hc平多
                            t0 = threading.Thread(target=query_paks.order_liquidation, args=(ACCESS_KEY, SECRET_KEY, "LONG"))
                            t0.start()
                            # xt平空
                            t2 = threading.Thread(target=close_all)
                            t2.start()
                            temp = {}
                            temp['hc'] = '平多'
                            temp['xt'] = '平空'
                            temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                            temp['xt卖一'] = self.xt_sell
                            temp['hc卖一'] = self.hc_sell
                            temp['hc卖一-xt卖一-平均值'] = (self.hc_sell - self.xt_sell) - hc_xt_sell_list_avg_price
                            t1 = threading.Thread(target=save_data, args=(temp, json_name))
                            t1.start()
                    pass

if __name__ == '__main__':
    multiprocessing.freeze_support()
    queue = Queue()
    work = Work(queue)
    three = Process(target=work.domian)
    three.start()
    three.join()
    # hc = hotcoin_wss(queue)
    # hc.connection_open_api()