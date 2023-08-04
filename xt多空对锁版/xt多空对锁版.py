import ssl
import websocket
import json
import time
import multiprocessing
import threading
from base_util_xt import open_order, close_all, get_xt_account, get_hold
from json_create import save_data
from multiprocessing import Manager, Process, Queue
import os,signal
from send_email import send_email
import random
json_name = "hc_xt_BTC日志.json"

try:
    with open('volume.json', encoding="utf-8") as file_obj:
        data_temp = json.load(file_obj)
    file_obj.close()
except Exception as e:
    print(e)

class binance_wss(object):

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
            ws.run_forever(ping_interval=30,sslopt={"cert_reqs": ssl.CERT_NONE})
        except:
            ws.close()
        return ws

class Work(object):

    def __init__(self, queue, List):
        self.queue = queue
        self.binance_price = 0
        self.binance_sell = 0
        self.binance_buy = 0
        self.xt_price = 0
        self.xt_sell = 0
        self.xt_buy = 0
        self.flag = 0
        self.profit = 15
        self.hc_volume = data_temp['hc_volume']
        self.xt_volume = data_temp['xt_volume']
        self.List = List

    def domian(self):
        tiaojian1 = 0
        tiaojian1_1 = 0
        tiaojian2 = 0
        tiaojian2_1 = 0
        time_end = 0
        chicang = 0
        work1 = binance_wss(self.queue)
        one = Process(target=work1.connection_open_api)

        work2 = xt_wss(self.queue)
        two = Process(target=work2.connection_open_api)

        one.start()
        two.start()

        pid = os.getpid()
        print(pid)
        # 风控1 统计本金是否充足
        fengkong = Process(target=self.fengkong, args=(pid,))
        fengkong.start()
        # 风控2 平仓信号处理
        fengkong2 = Process(target=self.close_check)
        fengkong2.start()

        bn_xt_buy_list = []
        bn_xt_sell_list = []
        LEN = 2000

        while True:
            data = self.queue.get()
            # 平仓信号发送
            self.List[0] = chicang
            # print(data)
            # bn的数据
            if data[1] == 0:
                self.binance_price = data[0][0]
            # xt的数据u
            else:
                self.xt_price = (data[0][0] + data[0][1]) / 2
                self.xt_sell = data[0][0]
                self.xt_buy = data[0][1]

            if len(bn_xt_buy_list) > LEN and len(bn_xt_sell_list) > LEN:
                del bn_xt_buy_list[0]
                del bn_xt_sell_list[0]

            if self.xt_price != 0 and self.binance_price != 0:
                bn_xt_buy_list.append(self.binance_price - self.xt_buy)
                bn_xt_sell_list.append(self.binance_price - self.xt_sell)
                bn_xt_buy_list_avg_price = sum(bn_xt_buy_list) / len(bn_xt_buy_list)
                bn_xt_sell_list_avg_price = sum(bn_xt_sell_list) / len(bn_xt_sell_list)
                print('bn最新价-xt买一的平均值', bn_xt_buy_list_avg_price, 'bn最新价-xt卖一的平均值',bn_xt_sell_list_avg_price, len(bn_xt_buy_list), len(bn_xt_sell_list))
            if self.xt_price != 0 and self.binance_price != 0 and len(bn_xt_buy_list) > LEN:
                print('bn最新价', self.binance_price, 'xt买一', self.xt_buy, 'xt卖一', 'bn最新价-xt买一-平均值',(self.binance_price - self.xt_buy) - bn_xt_buy_list_avg_price, 'bn最新价-xt卖一-平均值',(self.binance_price - self.xt_sell) - bn_xt_sell_list_avg_price)
            else:
                continue
            # xt开多
            if self.flag == 0 and tiaojian1 == 0:
                if time.time()-time_end > 10:
                    # xt开多  条件1
                    if (self.binance_price - self.xt_sell) - bn_xt_sell_list_avg_price > self.profit and abs(self.binance_price-self.xt_sell) < 100:
                        tiaojian1 = 1
                        self.flag = 1
                        chicang = 1
                        # xt开多
                        t2 = threading.Thread(target=open_order, args=('btc_usdt', self.xt_volume, 'BUY', 'LONG', 0))
                        t2.start()
                        temp = {}
                        temp['xt'] = '开多'
                        temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        temp['xt卖一'] = self.xt_sell
                        temp['bn最新价 - xt卖一-平均值'] = (self.binance_price - self.xt_sell) - bn_xt_sell_list_avg_price
                        t1 = threading.Thread(target=save_data, args=(temp, json_name))
                        t1.start()
                        pass
            # xt开多之后开空
            if self.flag == 1 and tiaojian1 == 1 and tiaojian1_1 == 0:
                # xt开空
                if (self.binance_price - self.xt_buy) - bn_xt_buy_list_avg_price < 5 and abs(self.binance_price-self.xt_buy) < 100:
                    time_start = time.time()
                    tiaojian1_1 = 1
                    chicang = 1
                    # xt开空
                    t2 = threading.Thread(target=open_order, args=('btc_usdt', self.xt_volume, 'SELL', 'SHORT', 0))
                    t2.start()
                    temp = {}
                    temp['xt'] = '开空'
                    temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    temp['xt买一'] = self.xt_buy
                    temp['bn最新价 - xt买一-平均值'] = (self.binance_price - self.xt_buy) - bn_xt_buy_list_avg_price
                    t1 = threading.Thread(target=save_data, args=(temp, json_name))
                    t1.start()
                    pass
            # xt开空
            if self.flag == 0 and tiaojian2 == 0:
                if time.time() - time_end > 10:
                    # xt开空
                    if (self.binance_price - self.xt_buy) - bn_xt_buy_list_avg_price < - self.profit and abs(self.binance_price - self.xt_buy) < 100:
                        tiaojian2 = 1
                        self.flag = 1
                        chicang = 1
                        # xt开空
                        t2 = threading.Thread(target=open_order, args=('btc_usdt', self.xt_volume, 'SELL', 'SHORT', 0))
                        t2.start()
                        temp = {}
                        temp['xt'] = '开空'
                        temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        temp['xt买一'] = self.xt_buy
                        temp['bn最新价 - xt买一-平均值'] = (self.binance_price - self.xt_buy) - bn_xt_buy_list_avg_price
                        t1 = threading.Thread(target=save_data, args=(temp, json_name))
                        t1.start()
                        pass
            # xt开空之后开多
            if self.flag == 1 and tiaojian2 == 1 and tiaojian2_1 == 0:
                if (self.binance_price - self.xt_sell) - bn_xt_sell_list_avg_price > - 5 and abs(self.binance_price - self.xt_sell) < 100:
                    tiaojian2_1 = 1
                    chicang = 1
                    time_start = time.time()
                    # xt开多
                    t2 = threading.Thread(target=open_order, args=('btc_usdt', self.xt_volume, 'BUY', 'LONG', 0))
                    t2.start()
                    temp = {}
                    temp['xt'] = '开多'
                    temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    temp['xt卖一'] = self.xt_buy
                    temp['bn最新价 - xt卖一-平均值'] = (self.binance_price - self.xt_sell) - bn_xt_sell_list_avg_price
                    t1 = threading.Thread(target=save_data, args=(temp, json_name))
                    t1.start()
                    pass

            # 平仓 平多
            if self.flag == 1 and tiaojian1_1 == 1:
                if time.time() - time_start > 300:
                    if tiaojian1 == 1:
                        # 持仓不能大于10分钟
                        if ((self.binance_price - self.xt_buy) - bn_xt_buy_list_avg_price < - self.profit and abs(self.binance_price - self.xt_buy) < 100):
                            tiaojian1 = 0
                            # xt平多
                            t2 = threading.Thread(target=open_order,args=('btc_usdt', self.xt_volume, 'SELL', 'LONG', 0))
                            t2.start()
                            temp = {}
                            temp['xt'] = '平多'
                            temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                            temp['xt买一'] = self.xt_buy
                            temp['bn最新价-xt买一-平均值'] = (self.binance_price - self.xt_buy) - bn_xt_buy_list_avg_price
                            t1 = threading.Thread(target=save_data, args=(temp, json_name))
                            t1.start()
            # 平多了之后平空
            if self.flag == 1 and tiaojian1_1 == 1 and tiaojian1 == 0:
                if (self.binance_price - self.xt_sell) - bn_xt_sell_list_avg_price > - 5 and abs(self.binance_price - self.xt_sell) < 100:
                    time_end = time.time()
                    tiaojian1_1 = 0
                    self.flag = 0
                    chicang = 0
                    # xt平空
                    t2 = threading.Thread(target=close_all)
                    t2.start()
                    temp = {}
                    temp['xt'] = '平空'
                    temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    temp['xt卖一'] = self.xt_sell
                    temp['bn最新价-xt卖一-平均值'] = (self.binance_price - self.xt_sell) - bn_xt_sell_list_avg_price
                    t1 = threading.Thread(target=save_data, args=(temp, json_name))
                    t1.start()
            # 平空
            if self.flag == 1 and tiaojian2_1 == 1:
                if time.time() - time_start > 300:
                    if tiaojian2 == 1:
                        if ((self.binance_price - self.xt_sell) - bn_xt_sell_list_avg_price > self.profit and abs(self.binance_price - self.xt_sell) < 100):
                            tiaojian2 = 0
                            # xt平空
                            t2 = threading.Thread(target=open_order,args=('btc_usdt', self.xt_volume, 'BUY', 'SHORT', 0))
                            t2.start()
                            temp = {}
                            temp['xt'] = '平空'
                            temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                            temp['xt卖一'] = self.xt_sell
                            temp['bn最新价-xt卖一-平均值'] = (self.binance_price - self.xt_sell) - bn_xt_sell_list_avg_price
                            t1 = threading.Thread(target=save_data, args=(temp, json_name))
                            t1.start()
            # 平空了之后平多
            if self.flag == 1 and tiaojian2_1 == 1 and tiaojian2 == 0:
                if (self.binance_price - self.xt_buy) - bn_xt_buy_list_avg_price < 5 and abs(self.binance_price - self.xt_buy) < 100:
                    time_end = time.time()
                    tiaojian2_1 = 0
                    self.flag = 0
                    chicang = 0
                    # xt平多
                    t2 = threading.Thread(target=close_all)
                    t2.start()
                    temp = {}
                    temp['xt'] = '平多'
                    temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    temp['xt买一'] = self.xt_buy
                    temp['bn最新价-xt买一-平均值'] = (self.binance_price - self.xt_buy) - bn_xt_buy_list_avg_price
                    t1 = threading.Thread(target=save_data, args=(temp, json_name))
                    t1.start()

    def fengkong(self, pids):
        while 1:
            time.sleep(10)
            # 查询hc的账户余额
            try:
                if get_xt_account() < 50:
                    print("资金不足")
                    close_all()
                    send_email('服务器214', '资金不足')
                    os.kill(pids, signal.SIGINT)
                else:
                    print("资金正常")
                    # os.kill(pids, signal.SIGINT)
            except:
                pass

    # 平仓检查
    def close_check(self):
        while 1:
            time.sleep(5)
            # 接收主要处理函数信号
            data = self.List
            chicang = data[0]
            # 如果是处于无仓位信号的话，检查仓位是否平仓掉
            if chicang == 0:
                try:
                    response = get_hold()
                except Exception as e:
                    print(e)
                # 平仓失败继续平仓
                if response > 0:
                    close_all()
                else:
                    print('没有持仓！！！！！！！！！！！！！！！！')
            else:
                print("持仓中！！！！！！！！！！！！！！！！！！！")

if __name__ == '__main__':
    multiprocessing.freeze_support()
    queue = Queue()
    List = Manager().list()
    List.append(0)
    work = Work(queue, List)
    three = Process(target=work.domian)
    three.start()
    three.join()